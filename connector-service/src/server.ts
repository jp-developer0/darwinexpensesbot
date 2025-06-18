import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import config from './config.js';
import logger from './logger.js';
import TelegramBotHandler from './telegramBot.js';
import { WebhookRequest } from './types.js';

class Server {
  private app: express.Application;
  private telegramBot: TelegramBotHandler;

  constructor() {
    this.app = express();
    this.telegramBot = new TelegramBotHandler();
    this.setupMiddleware();
    this.setupRoutes();
  }

  /**
   * Setup Express middleware
   */
  private setupMiddleware(): void {
    // Security middleware
    this.app.use(helmet());
    
    // CORS middleware
    this.app.use(cors());
    
    // Body parsing middleware
    this.app.use(express.json({ limit: '1mb' }));
    this.app.use(express.urlencoded({ extended: true }));

    // Request logging middleware
    this.app.use((req, _res, next) => {
      logger.info(`${req.method} ${req.path} - ${req.ip}`);
      next();
    });
  }

  /**
   * Setup Express routes
   */
  private setupRoutes(): void {
    // Health check endpoint
    this.app.get('/health', (_req, res) => {
      res.json({
        status: 'healthy',
        service: 'connector-service',
        timestamp: new Date().toISOString(),
      });
    });

    // Webhook endpoint for Telegram
    this.app.post('/webhook', (req, res) => this.handleWebhook(req as any, res));

    // Bot information endpoint
    this.app.get('/bot-info', this.getBotInfo.bind(this));

    // Setup webhook endpoint
    this.app.post('/setup-webhook', this.setupWebhook.bind(this));

    // Remove webhook endpoint
    this.app.delete('/webhook', this.removeWebhook.bind(this));

    // Add user to whitelist endpoint
    this.app.post('/add-user/:telegramId', this.addUser.bind(this));

    // Catch-all route
    this.app.use('*', (_req, res) => {
      res.status(404).json({ error: 'Route not found' });
    });

    // Error handling middleware
    this.app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
      logger.error('Unhandled error:', err);
      res.status(500).json({ error: 'Internal server error' });
    });
  }

  /**
   * Handle incoming webhook requests from Telegram
   */
  private async handleWebhook(req: WebhookRequest, res: express.Response): Promise<void> {
    try {
      // Verify webhook secret if configured
      if (config.telegram.webhookSecret) {
        const receivedSecret = req.headers['x-telegram-bot-api-secret-token'];
        if (receivedSecret !== config.telegram.webhookSecret) {
          logger.warn('Invalid webhook secret received');
          res.status(401).json({ error: 'Unauthorized' });
          return;
        }
      }

      const update = req.body;
      logger.debug('Received webhook update:', JSON.stringify(update));

      // Process the update through the Telegram bot handler
      await this.telegramBot.processWebhookUpdate(update as any);

      res.status(200).json({ ok: true });
    } catch (error) {
      logger.error('Error handling webhook:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  /**
   * Get bot information
   */
  private async getBotInfo(req: express.Request, res: express.Response): Promise<void> {
    try {
      const botInfo = await this.telegramBot.getBotInfo();
      res.json({ bot: botInfo });
    } catch (error) {
      logger.error('Error getting bot info:', error);
      res.status(500).json({ error: 'Failed to get bot information' });
    }
  }

  /**
   * Setup webhook
   */
  private async setupWebhook(req: express.Request, res: express.Response): Promise<void> {
    try {
      await this.telegramBot.setupWebhook();
      res.json({ message: 'Webhook setup successfully' });
    } catch (error) {
      logger.error('Error setting up webhook:', error);
      res.status(500).json({ error: 'Failed to setup webhook' });
    }
  }

  /**
   * Remove webhook
   */
  private async removeWebhook(req: express.Request, res: express.Response): Promise<void> {
    try {
      await this.telegramBot.removeWebhook();
      res.json({ message: 'Webhook removed successfully' });
    } catch (error) {
      logger.error('Error removing webhook:', error);
      res.status(500).json({ error: 'Failed to remove webhook' });
    }
  }

  /**
   * Add user to whitelist
   */
  private async addUser(req: express.Request, res: express.Response): Promise<void> {
    try {
      const { telegramId } = req.params;
      
      if (!telegramId) {
        res.status(400).json({ error: 'Telegram ID is required' });
        return;
      }

      // Note: This endpoint forwards the request to the Bot Service
      // In a production environment, you might want to add authentication here
      res.json({ 
        message: 'To add a user to the whitelist, use the Bot Service API directly',
        botServiceUrl: `${config.botService.url}/add-user?telegram_id=${telegramId}`
      });
    } catch (error) {
      logger.error('Error in add user endpoint:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  /**
   * Start the server
   */
  async start(): Promise<void> {
    return new Promise((resolve) => {
      this.app.listen(config.server.port, () => {
        logger.info(`Connector Service started on port ${config.server.port}`);
        logger.info(`Health check available at: http://localhost:${config.server.port}/health`);
        
        if (config.telegram.webhookUrl) {
          logger.info(`Webhook endpoint: ${config.telegram.webhookUrl}`);
        } else {
          logger.info('Running in polling mode');
        }
        
        resolve();
      });
    });
  }

  /**
   * Stop the server
   */
  stop(): void {
    this.telegramBot.stop();
    logger.info('Connector Service stopped');
  }
}

export default Server; 