# Connector Service - Telegram Expense Bot

Node.js service that interfaces with the Telegram API and forwards messages to the Bot Service for processing.

## Features

- 🤖 Telegram Bot API integration with webhook and polling support
- 🔗 HTTP client for Bot Service communication
- 🚀 Express.js server with TypeScript
- 📱 Webhook endpoint for production deployments
- 🔄 Polling mode for development
- 🛡️ Security middleware (Helmet, CORS)
- 📝 Comprehensive logging with Winston
- ⚡ Graceful shutdown handling

## Requirements

- Node.js 18+ (LTS)
- Telegram Bot Token (from @BotFather)
- Running Bot Service instance

## Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

3. Build the project:
```bash
npm run build
```

## Configuration

Create a `.env` file with the following variables:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
WEBHOOK_URL=https://your-domain.com/webhook

# Bot Service Configuration
BOT_SERVICE_URL=http://localhost:8000

# Server Configuration
PORT=3000
NODE_ENV=development

# Webhook Configuration (optional)
WEBHOOK_SECRET=your_webhook_secret_here
```

### Getting a Telegram Bot Token

1. Message @BotFather on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token to your `.env` file

## Running the Service

### Development (with polling)
```bash
npm run dev
```

### Production (with webhook)
```bash
npm start
```

## Deployment Modes

### Polling Mode (Development)
- Suitable for development and testing
- No webhook URL required
- Bot polls Telegram for updates
- Enabled when `WEBHOOK_URL` is not set

### Webhook Mode (Production)
- Recommended for production
- Requires HTTPS endpoint
- More efficient than polling
- Set `WEBHOOK_URL` in environment variables

## API Endpoints

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "connector-service",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### POST `/webhook`
Telegram webhook endpoint (only used in webhook mode).

### GET `/bot-info`
Get Telegram bot information.

**Response:**
```json
{
  "bot": {
    "id": 123456789,
    "is_bot": true,
    "first_name": "ExpenseBot",
    "username": "your_expense_bot"
  }
}
```

### POST `/setup-webhook`
Setup Telegram webhook (call once when deploying).

### DELETE `/webhook`
Remove Telegram webhook.

### POST `/add-user/:telegramId`
Information about adding users to whitelist.

## Bot Service Communication

The Connector Service communicates with the Bot Service via HTTP:

- **Endpoint**: `POST {BOT_SERVICE_URL}/process-message`
- **Request**: `{ "message": "Pizza 20 bucks", "telegram_id": "123456789" }`
- **Response**: `{ "success": true, "message": "Food expense added ✅", "expense_added": true, "category": "Food" }`

## Message Flow

1. User sends message to Telegram bot
2. Telegram delivers message via webhook or polling
3. Connector Service receives message
4. Connector Service forwards to Bot Service
5. Bot Service processes and responds
6. Connector Service sends response back to user

## Error Handling

- **Bot Service unavailable**: Falls back to error message
- **Invalid webhook secret**: Returns 401 Unauthorized
- **Telegram API errors**: Logged and handled gracefully
- **Unhandled exceptions**: Logged and service restarts

## Logging

Logs are written to:
- `logs/error.log` - Error level logs
- `logs/combined.log` - All logs
- Console (in development)

Log levels:
- `error`: Critical errors
- `warn`: Warning conditions
- `info`: General information
- `debug`: Debug information (development only)

## Development

### Project Structure
```
src/
├── config.ts       # Configuration management
├── logger.ts       # Winston logger setup
├── types.ts        # TypeScript interfaces
├── botService.ts   # Bot Service HTTP client
├── telegramBot.ts  # Telegram bot handler
├── server.ts       # Express server
└── index.ts        # Main entry point
```

### Scripts
```bash
npm run dev         # Development with hot reload
npm run build       # Build TypeScript
npm run start       # Start production server
npm run lint        # Run ESLint
npm run format      # Format code with Prettier
npm run clean       # Clean build directory
```

### TypeScript Configuration
- **Target**: ES2022
- **Module**: ESNext (native ES modules)
- **Strict mode**: Enabled
- **Source maps**: Generated

## Production Deployment

### Environment Setup
1. Set `NODE_ENV=production`
2. Configure `WEBHOOK_URL` with your domain
3. Set up HTTPS endpoint
4. Configure `WEBHOOK_SECRET` for security

### Webhook Setup
After deployment, setup the webhook:
```bash
curl -X POST https://your-domain.com/setup-webhook
```

### Health Monitoring
Monitor the service using:
- Health endpoint: `GET /health`
- Log files in `logs/` directory
- Process monitoring (PM2, systemd, etc.)

### Using Docker
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY dist ./dist
CMD ["node", "dist/index.js"]
```

### Using PM2
```bash
npm install -g pm2
pm2 start dist/index.js --name telegram-connector
pm2 startup
pm2 save
```

## Security

- **Webhook secret verification**: Validates incoming webhooks
- **CORS protection**: Configurable origins
- **Helmet.js**: Security headers
- **Input validation**: All inputs validated
- **Error sanitization**: No sensitive data in responses

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check `TELEGRAM_BOT_TOKEN` is correct
   - Verify Bot Service is running
   - Check logs for errors

2. **Webhook not working**
   - Ensure `WEBHOOK_URL` is HTTPS
   - Verify webhook is set up: `GET /bot-info`
   - Check webhook secret matches

3. **Bot Service connection failed**
   - Verify `BOT_SERVICE_URL` is correct
   - Check Bot Service health: `GET {BOT_SERVICE_URL}/health`
   - Review network connectivity

### Debug Mode
Set `NODE_ENV=development` for detailed debug logs.

## Testing

### Manual Testing
1. Start both services
2. Send message to your Telegram bot
3. Check logs for message flow
4. Verify expense is added to database

### Using cURL
```bash
# Test webhook endpoint
curl -X POST https://your-domain.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"update_id":1,"message":{"message_id":1,"from":{"id":123},"chat":{"id":123},"date":1234567890,"text":"test"}}'
```

## License

MIT 