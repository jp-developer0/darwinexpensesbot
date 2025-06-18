import axios from 'axios';
import config from './config.js';
import logger from './logger.js';
import { ProcessMessageRequest, ProcessMessageResponse } from './types.js';

class BotServiceClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = config.botService.url;
  }

  /**
   * Process a message through the Bot Service
   */
  async processMessage(message: string, telegramId: string): Promise<ProcessMessageResponse> {
    try {
      const request: ProcessMessageRequest = {
        message,
        telegram_id: telegramId,
      };

      logger.info(`Sending message to Bot Service: ${message} from user ${telegramId}`);

      const response = await axios.post<ProcessMessageResponse>(
        `${this.baseUrl}/process-message`,
        request,
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 30000, // 30 second timeout
        }
      );

      logger.info(`Bot Service response: ${JSON.stringify(response.data)}`);
      return response.data;

    } catch (error) {
      logger.error('Error communicating with Bot Service:', error);
      
      if (axios.isAxiosError(error)) {
        if (error.response) {
          logger.error(`Bot Service returned error: ${error.response.status} - ${error.response.data}`);
        } else if (error.request) {
          logger.error('No response from Bot Service');
        } else {
          logger.error(`Request setup error: ${error.message}`);
        }
      }

      // Return a fallback response
      return {
        success: false,
        message: 'Sorry, I\'m having trouble processing your request right now. Please try again later.',
        expense_added: false,
      };
    }
  }

  /**
   * Health check for the Bot Service
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseUrl}/health`, {
        timeout: 5000,
      });
      return response.status === 200;
    } catch (error) {
      logger.error('Bot Service health check failed:', error);
      return false;
    }
  }

  /**
   * Add a user to the Bot Service whitelist
   */
  async addUser(telegramId: string): Promise<boolean> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/add-user`,
        null,
        {
          params: { telegram_id: telegramId },
          timeout: 10000,
        }
      );
      
      logger.info(`User ${telegramId} added to whitelist: ${JSON.stringify(response.data)}`);
      return response.status === 200;
    } catch (error) {
      logger.error(`Error adding user ${telegramId} to whitelist:`, error);
      return false;
    }
  }
}

export default new BotServiceClient(); 