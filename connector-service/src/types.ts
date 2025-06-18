// Bot Service API types
export interface ProcessMessageRequest {
  message: string;
  telegram_id: string;
}

export interface ProcessMessageResponse {
  success: boolean;
  message: string;
  expense_added: boolean;
  category?: string;
}

// Telegram types
export interface TelegramMessage {
  message_id: number;
  from?: {
    id: number;
    is_bot: boolean;
    first_name: string;
    last_name?: string;
    username?: string;
  };
  chat: {
    id: number;
    first_name?: string;
    last_name?: string;
    username?: string;
    type: string;
  };
  date: number;
  text?: string;
}

export interface TelegramUpdate {
  update_id: number;
  message?: TelegramMessage;
}

// Express types for webhook
export interface WebhookRequest {
  body: TelegramUpdate;
  headers: {
    'x-telegram-bot-api-secret-token'?: string;
  };
} 