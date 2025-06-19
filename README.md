# Telegram Expense Bot 💰

A modern Telegram chatbot system that uses **Google Gemini AI** to analyze and categorize expenses through natural language messages.

## ✨ Features

- 🤖 **AI-Powered Categorization**: Uses Google Gemini 2.0 Flash for intelligent expense categorization
- 📊 **Smart Categories**: Automatically categorizes expenses into Housing, Food, Transportation, etc.
- 🔒 **User Whitelisting**: Secure access control
- ☁️ **Cloud Database**: Uses Supabase for reliable data storage
- 🐳 **Docker Ready**: Easy deployment with Docker Compose
- 📱 **Natural Language**: Send messages like "Pizza $20" or "Gas station 45 dollars"

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Telegram Bot   │───▶│ Connector Service │───▶│   Bot Service   │
│                 │    │    (Node.js)     │    │   (Python)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │  Google Gemini  │
                                               │       AI        │
                                               └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │    Supabase     │
                                               │   PostgreSQL    │
                                               └─────────────────┘
```

- **Connector Service**: Handles Telegram webhook and forwards messages
- **Bot Service**: Processes messages using Gemini AI and stores in database
- **Google Gemini**: Provides intelligent expense categorization
- **Supabase**: Cloud PostgreSQL database for data persistence

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Google AI API key ([Get one here](https://makersuite.google.com/app/apikey))
- Telegram Bot Token ([Create via @BotFather](https://t.me/botfather))
- Supabase account ([Sign up here](https://supabase.com))

### 1. Setup Supabase Database

1. Create a new Supabase project
2. Go to SQL Editor in your dashboard
3. Run the SQL commands from `supabase-setup.sql`
4. Get your database credentials from Project Settings → Database

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBHOOK_URL=https://your-domain.com/webhook  # Optional for production

# AI Configuration  
GOOGLE_API_KEY=your_google_api_key_here

# Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres

# Security
WEBHOOK_SECRET=your_webhook_secret_here
```

### 3. Deploy

```bash
# Start all services
docker-compose up -d

# Add yourself to whitelist (replace with your Telegram ID)
curl -X POST "http://localhost:8000/add-user?telegram_id=YOUR_TELEGRAM_ID"
```

### 4. Test

Send a message to your bot:
- "Pizza $20" → Gets categorized as **Food**
- "Gas station 45 dollars" → Gets categorized as **Transportation** 
- "Rent payment 1200" → Gets categorized as **Housing**

## 📋 Expense Categories

The AI automatically categorizes expenses into:

| Category | Examples |
|----------|----------|
| **Food** | Pizza, groceries, restaurants, coffee |
| **Transportation** | Gas, car payments, taxi, parking |
| **Housing** | Rent, mortgage, utilities, furniture |
| **Entertainment** | Movies, games, concerts, streaming |
| **Medical/Healthcare** | Doctor visits, medicine, dental |
| **Education** | Tuition, books, courses |
| **Utilities** | Electricity, water, internet |
| **Insurance** | Health, car, home insurance |
| **Savings** | Investments, savings accounts |
| **Debt** | Loan payments, credit cards |
| **Other** | Anything that doesn't fit above |

## 🛠️ Development

### Services

- **Bot Service** (Python): [`./bot-service/`](./bot-service/)
- **Connector Service** (Node.js): [`./connector-service/`](./connector-service/)

### Local Development

```bash
# Bot Service
cd bot-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Connector Service  
cd connector-service
npm install
npm run dev
```

### Database Schema

See [`supabase-setup.sql`](./supabase-setup.sql) for the complete database schema including:
- Users table for whitelisting
- Expenses table for transaction storage
- Views for analytics
- Row Level Security policies

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | ✅ |
| `GOOGLE_API_KEY` | Google AI API key | ✅ |
| `DATABASE_URL` | Supabase PostgreSQL connection string | ✅ |
| `WEBHOOK_URL` | Public URL for Telegram webhook | ⚠️ Production only |
| `WEBHOOK_SECRET` | Security token for webhooks | ⚠️ Production only |

### Docker Configuration

The services use host networking mode for external API connectivity. Ports:
- **Bot Service**: 8000
- **Connector Service**: 3000

## 📊 API Endpoints

### Bot Service (`localhost:8000`)

- `GET /health` - Health check
- `POST /process-message` - Process expense message
- `POST /add-user?telegram_id={id}` - Add user to whitelist
- `GET /users/{telegram_id}` - Get user information

### Connector Service (`localhost:3000`)

- `GET /health` - Health check  
- `POST /webhook` - Telegram webhook endpoint

## 🔍 Monitoring

Check service logs:

```bash
# View all logs
docker-compose logs

# View specific service
docker-compose logs bot-service
docker-compose logs connector-service
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using Google Gemini AI, Supabase, and Docker** 