# Telegram Expense Bot

A Telegram chatbot system that facilitates adding expenses to a database through natural language messages.

## Architecture

The system consists of two services:

- **Bot Service** (Python): Analyzes incoming messages using LangChain and LLM to extract expense details and categorize them
- **Connector Service** (Node.js): Interfaces with Telegram API and forwards messages to the Bot Service

**Database**: Uses Supabase (hosted PostgreSQL) for data storage.

## Services

### [Bot Service](./bot-service)
Python service that processes expense messages and stores them in Supabase.

### [Connector Service](./connector-service)  
Node.js service that handles Telegram webhook and communicates with the Bot Service.

## Database Schema

```sql
CREATE TABLE users (
  "id" SERIAL PRIMARY KEY,
  "telegram_id" text UNIQUE NOT NULL
);

CREATE TABLE expenses (
  "id" SERIAL PRIMARY KEY,
  "user_id" integer NOT NULL REFERENCES users("id"),
  "description" text NOT NULL,
  "amount" money NOT NULL,
  "category" text NOT NULL,
  "added_at" timestamp NOT NULL
);
```

## Quick Start

### 1. Prerequisites
- Docker and Docker Compose (recommended)
- OR: Python 3.11+, Node.js 18+
- Telegram Bot Token (from @BotFather)
- OpenAI API Key
- Supabase account and project

### 2. Setup Supabase Database

1. Create a Supabase account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to the SQL Editor in your Supabase dashboard
4. Copy and run the SQL commands from `supabase-setup.sql` to set up the database schema
5. Get your database credentials from Project Settings > Database

### 3. Get Telegram Bot Token
1. Message @BotFather on Telegram
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token

### 4. Setup with Docker (Recommended)

1. Clone and setup:
```bash
git clone <repository-url>
cd telegram-expense-bot
cp env.example .env
```

2. Edit `.env` with your credentials:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://postgres:YOUR_SUPABASE_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres
WEBHOOK_URL=https://your-domain.com/webhook  # Optional for production
```

3. Start all services:
```bash
docker-compose up -d
```

4. Add yourself to the whitelist:
```bash
curl -X POST "http://localhost:8000/add-user?telegram_id=YOUR_TELEGRAM_ID"
```

### 5. Manual Setup (Alternative)

1. Setup Bot Service:
```bash
cd bot-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your Supabase configuration
python main.py
```

2. Setup Connector Service:
```bash
cd connector-service
npm install
npm run build
cp env.example .env
# Edit .env with your configuration
npm start
```

### 6. Testing
1. Send a message to your Telegram bot: "Pizza $20"
2. Bot should respond: "Food expense added ✅"
3. Check logs and Supabase database for the recorded expense

See individual service READMEs for detailed setup instructions.

## Expense Categories

The bot automatically categorizes expenses into:
- Housing
- Transportation  
- Food
- Utilities
- Insurance
- Medical/Healthcare
- Savings
- Debt
- Education
- Entertainment
- Other

## Usage

Users send messages like:
- "Pizza 20 bucks"
- "Gas station $45"
- "Rent payment 1200"

The bot responds with: "[Category] expense added ✅" 