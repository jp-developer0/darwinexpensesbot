# Connector Service 🔌

The Node.js service that handles Telegram bot integration and forwards messages to the Bot Service for AI processing.

## 🚀 Features

- **Telegram Integration**: Full webhook and polling support
- **Message Routing**: Forwards user messages to Bot Service
- **Error Handling**: Robust error management and logging
- **TypeScript**: Type-safe development with modern ES modules
- **Production Ready**: Express.js with comprehensive middleware
- **Docker Support**: Containerized deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Telegram API   │───▶│ Connector Service │───▶│   Bot Service   │
│   (Webhooks)    │    │    (Node.js)     │    │    (Python)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Events   │    │   HTTP Routing   │    │ AI Processing   │
│   & Messages    │    │   & Validation   │    │ & Storage       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
connector-service/
├── src/
│   ├── index.ts         # Application entry point
│   ├── server.ts        # Express server setup
│   ├── telegramBot.ts   # Telegram bot logic
│   ├── botService.ts    # Bot service client
│   ├── config.ts        # Configuration management
│   ├── logger.ts        # Logging utilities
│   └── types.ts         # TypeScript type definitions
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript configuration
└── Dockerfile          # Container configuration
```

## 🛠️ Development

### Local Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Environment Configuration**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export BOT_SERVICE_URL="http://localhost:8000"
   export PORT="3000"
   export NODE_ENV="development"
   ```

3. **Development Mode**
   ```bash
   npm run dev
   ```

4. **Production Build**
   ```bash
   npm run build
   npm start
   ```

### Docker

```bash
# Build image
docker build -t expense-connector-service .

# Run container
docker run -p 3000:3000 \
  -e TELEGRAM_BOT_TOKEN="your_bot_token" \
  -e BOT_SERVICE_URL="http://localhost:8000" \
  expense-connector-service
```

## 📊 API Endpoints

### Health Check
```http
GET /health
```
Returns service status and version.

### Telegram Webhook
```http
POST /webhook
Content-Type: application/json

{
  "message": {
    "from": { "id": 123456789 },
    "text": "Pizza $20"
  }
}
```

Processes incoming Telegram messages and forwards to Bot Service.

## 🤖 Telegram Bot Integration

### Webhook Configuration

The service automatically configures the Telegram webhook:

```typescript
// Webhook setup
await bot.telegram.setWebhook(`${config.webhookUrl}/webhook`, {
  secret_token: config.webhookSecret
});
```

### Message Processing Flow

1. **Receive**: Telegram sends webhook to `/webhook`
2. **Validate**: Check message format and user
3. **Forward**: Send to Bot Service for AI processing
4. **Respond**: Return processed result to user

### Bot Commands

- `/start` - Welcome message and instructions
- `/help` - Usage instructions and examples
- Regular messages - Processed as expense data

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | - | ✅ |
| `BOT_SERVICE_URL` | Bot service endpoint | `http://localhost:8000` | ✅ |
| `WEBHOOK_URL` | Public webhook URL | - | Production only |
| `WEBHOOK_SECRET` | Webhook security token | - | Production only |
| `PORT` | Service port | `3000` | ❌ |
| `NODE_ENV` | Environment mode | `development` | ❌ |

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

## 🔄 Message Flow

### Incoming Message Processing

```typescript
// 1. Receive webhook
app.post('/webhook', (req, res) => {
  const update = req.body;
  
  // 2. Extract message data
  const message = update.message?.text;
  const telegramId = update.message?.from?.id;
  
  // 3. Forward to Bot Service
  const response = await botService.processMessage({
    message,
    telegram_id: telegramId.toString()
  });
  
  // 4. Send response to user
  await bot.telegram.sendMessage(telegramId, response.message);
});
```

### Error Handling

- **Network Errors**: Retry logic with exponential backoff
- **Invalid Messages**: Graceful error responses
- **Bot Service Unavailable**: Fallback error messages
- **Rate Limiting**: Telegram API rate limit handling

## 📝 Logging

### Structured Logging

```typescript
// Log levels: error, warn, info, debug
logger.info('Processing message', {
  telegramId,
  messageLength: message.length,
  timestamp: new Date().toISOString()
});
```

### Log Output

```
2024-01-15 10:30:15 [INFO] Processing message for user 123456789
2024-01-15 10:30:16 [INFO] Bot service response: Food expense added ✅
2024-01-15 10:30:16 [INFO] Message sent to user successfully
```

## 🧪 Testing

### Manual Testing

```bash
# Check service health
curl http://localhost:3000/health

# Test webhook (simulate Telegram)
curl -X POST "http://localhost:3000/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "from": {"id": 123456789},
      "text": "Pizza $20"
    }
  }'
```

### Integration Testing

1. **Start Services**: Both connector and bot services
2. **Send Message**: Via Telegram or webhook
3. **Verify Response**: Check user receives confirmation
4. **Check Database**: Verify expense was stored

## 🔒 Security

### Webhook Security

- **Secret Token**: Validates webhook authenticity
- **HTTPS Only**: Production webhooks use SSL
- **Rate Limiting**: Protection against spam
- **Input Validation**: Sanitize all incoming data

### Best Practices

```typescript
// Validate webhook secret
if (req.headers['x-telegram-bot-api-secret-token'] !== config.webhookSecret) {
  return res.status(401).send('Unauthorized');
}

// Sanitize message content
const sanitizedMessage = message.trim().substring(0, 1000);
```

## 🚀 Deployment

### Production Considerations

1. **Environment**: Set `NODE_ENV=production`
2. **Webhook URL**: Must be HTTPS endpoint
3. **Error Monitoring**: Use service like Sentry
4. **Load Balancing**: Multiple instances for scaling
5. **Health Checks**: Monitor `/health` endpoint

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist/ ./dist/
EXPOSE 3000
CMD ["npm", "start"]
```

## 📊 Monitoring

### Health Monitoring

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "connector-service",
  "uptime": "2h 15m 30s",
  "botServiceStatus": "connected"
}
```

### Metrics

- **Message Volume**: Messages processed per minute
- **Response Time**: Bot service response latency
- **Error Rate**: Failed message processing percentage
- **Uptime**: Service availability metrics

## 🔧 Dependencies

### Core Dependencies

- **Express**: Web framework
- **Telegraf**: Telegram bot framework
- **Axios**: HTTP client for bot service
- **Winston**: Logging library
- **TypeScript**: Type safety

### Development

```bash
# Install dev dependencies
npm install --save-dev @types/node ts-node nodemon

# Run linting
npm run lint

# Type checking
npm run type-check
```

## 🆘 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Bot not responding | Check `TELEGRAM_BOT_TOKEN` |
| Webhook fails | Verify `WEBHOOK_URL` is HTTPS |
| Bot service unreachable | Check `BOT_SERVICE_URL` |
| Messages not processed | Check bot service logs |

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=debug
npm run dev
```

---

**Built with TypeScript, Express, and Telegraf** 🚀 