import dotenv from 'dotenv';

dotenv.config();

interface Config {
  telegram: {
    botToken: string;
    webhookUrl?: string;
    webhookSecret?: string;
  };
  botService: {
    url: string;
  };
  server: {
    port: number;
    nodeEnv: string;
  };
}

const config: Config = {
  telegram: {
    botToken: process.env.TELEGRAM_BOT_TOKEN || '',
    webhookUrl: process.env.WEBHOOK_URL || undefined,
    webhookSecret: process.env.WEBHOOK_SECRET || undefined,
  },
  botService: {
    url: process.env.BOT_SERVICE_URL || 'http://localhost:8000',
  },
  server: {
    port: parseInt(process.env.PORT || '3000', 10),
    nodeEnv: process.env.NODE_ENV || 'development',
  },
};

// Validate required configuration
if (!config.telegram.botToken) {
  throw new Error('TELEGRAM_BOT_TOKEN is required');
}

if (!config.botService.url) {
  throw new Error('BOT_SERVICE_URL is required');
}

export default config; 