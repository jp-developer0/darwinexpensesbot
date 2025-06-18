import TelegramBot from 'node-telegram-bot-api';
import config from './config.js';
import logger from './logger.js';
import botService from './botService.js';

class TelegramBotHandler {
  private bot: TelegramBot;
  private isWebhookMode: boolean;

  constructor() {
    this.bot = new TelegramBot(config.telegram.botToken, {
      polling: !config.telegram.webhookUrl, // Only use polling if no webhook URL
    });
    this.isWebhookMode = !!config.telegram.webhookUrl;
    this.setupEventHandlers();
  }

  /**
   * Setup event handlers for the Telegram bot
   */
  private setupEventHandlers(): void {
    // Handle incoming messages
    this.bot.on('message', this.handleMessage.bind(this));

    // Handle polling errors
    this.bot.on('polling_error', (error) => {
      logger.error('Polling error:', error);
    });

    // Handle webhook errors
    this.bot.on('webhook_error', (error) => {
      logger.error('Webhook error:', error);
    });

    logger.info(`Telegram bot initialized in ${this.isWebhookMode ? 'webhook' : 'polling'} mode`);
  }

  /**
   * Handle incoming Telegram messages
   */
  private async handleMessage(msg: TelegramBot.Message): Promise<void> {
    try {
      const chatId = msg.chat.id;
      const userId = msg.from?.id?.toString();
      const messageText = msg.text;

      if (!userId) {
        logger.warn('Received message without user ID');
        return;
      }

      if (!messageText) {
        logger.debug(`Received non-text message from user ${userId}`);
        await this.bot.sendMessage(chatId, 'Please send me text messages with your expenses.');
        return;
      }

      logger.info(`Received message from user ${userId}: ${messageText}`);

      // Send typing indicator
      await this.bot.sendChatAction(chatId, 'typing');

      // Process message through Bot Service
      const response = await botService.processMessage(messageText, userId);

      // Send response back to user
      await this.bot.sendMessage(chatId, response.message, {
        parse_mode: 'Markdown',
      });

      if (response.expense_added && response.category) {
        logger.info(`Expense added for user ${userId}: ${response.category}`);
      }

    } catch (error) {
      logger.error('Error handling message:', error);
      
      if (msg.chat?.id) {
        try {
          await this.bot.sendMessage(
            msg.chat.id,
            'Sorry, something went wrong. Please try again later.'
          );
        } catch (sendError) {
          logger.error('Error sending error message:', sendError);
        }
      }
    }
  }

  /**
   * Process webhook update (for webhook mode)
   */
  async processWebhookUpdate(update: TelegramBot.Update): Promise<void> {
    try {
      await this.bot.processUpdate(update);
    } catch (error) {
      logger.error('Error processing webhook update:', error);
    }
  }

  /**
   * Set up webhook (call this when using webhook mode)
   */
  async setupWebhook(): Promise<void> {
    if (!this.isWebhookMode || !config.telegram.webhookUrl) {
      throw new Error('Webhook URL not configured');
    }

    try {
      const webhookOptions: TelegramBot.SetWebHookOptions = {
        url: config.telegram.webhookUrl,
      };

      if (config.telegram.webhookSecret) {
        webhookOptions.secret_token = config.telegram.webhookSecret;
      }

      await this.bot.setWebHook(config.telegram.webhookUrl, webhookOptions);
      logger.info(`Webhook set up successfully: ${config.telegram.webhookUrl}`);
    } catch (error) {
      logger.error('Error setting up webhook:', error);
      throw error;
    }
  }

  /**
   * Remove webhook (useful for switching to polling mode)
   */
  async removeWebhook(): Promise<void> {
    try {
      await this.bot.deleteWebHook();
      logger.info('Webhook removed successfully');
    } catch (error) {
      logger.error('Error removing webhook:', error);
      throw error;
    }
  }

  /**
   * Get bot information
   */
  async getBotInfo(): Promise<TelegramBot.User> {
    return await this.bot.getMe();
  }

  /**
   * Send a message to a specific chat
   */
  async sendMessage(chatId: number, text: string): Promise<TelegramBot.Message> {
    return await this.bot.sendMessage(chatId, text);
  }

  /**
   * Stop the bot
   */
  stop(): void {
    if (!this.isWebhookMode) {
      this.bot.stopPolling();
    }
    logger.info('Telegram bot stopped');
  }
}

export default TelegramBotHandler; 