# Bot Service - Telegram Expense Bot

Python service that processes expense messages using LangChain and OpenAI to extract expense details and store them in PostgreSQL.

## Features

- 🤖 LangChain integration with OpenAI for intelligent expense extraction
- 📊 Automatic expense categorization (Housing, Transportation, Food, etc.)
- 🔐 User whitelist validation
- 🐘 PostgreSQL database integration with connection pooling
- ⚡ Async FastAPI with concurrent request handling
- 📝 Comprehensive logging and error handling
- 🛡️ Robust fallback mechanisms for expense parsing

## Requirements

- Python 3.11+
- PostgreSQL database
- OpenAI API key

## Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

## Configuration

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/expense_bot

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Service Configuration
BOT_SERVICE_HOST=0.0.0.0
BOT_SERVICE_PORT=8000
```

## Database Setup

Create the required tables in your PostgreSQL database:

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

## Running the Service

### Development
```bash
python main.py
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST `/process-message`
Process a message to extract expense information.

**Request Body:**
```json
{
  "message": "Pizza 20 bucks",
  "telegram_id": "123456789"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Food expense added ✅",
  "expense_added": true,
  "category": "Food"
}
```

### POST `/add-user`
Add a user to the whitelist.

**Query Parameter:**
- `telegram_id`: Telegram user ID to add

**Response:**
```json
{
  "message": "User added successfully",
  "user": {
    "id": 1,
    "telegram_id": "123456789"
  }
}
```

### GET `/users/{telegram_id}`
Get user information by Telegram ID.

### GET `/health`
Health check endpoint.

## Expense Categories

The service automatically categorizes expenses into:

- **Housing**: Rent, mortgage, utilities related to housing
- **Transportation**: Gas, public transport, car maintenance
- **Food**: Groceries, restaurants, food delivery
- **Utilities**: Electricity, water, internet, phone
- **Insurance**: Health, car, home insurance
- **Medical/Healthcare**: Doctor visits, medications, medical bills
- **Savings**: Investments, savings deposits
- **Debt**: Loan payments, credit card payments
- **Education**: Tuition, books, courses
- **Entertainment**: Movies, games, subscriptions
- **Other**: Everything else

## LangChain Integration

The service uses LangChain with OpenAI's GPT-3.5-turbo-instruct to:

1. Analyze if a message contains an expense
2. Extract expense description, amount, and category
3. Provide fallback parsing for robustness

### Example Message Processing

- Input: "Pizza 20 bucks"
- Output: `{"is_expense": true, "description": "Pizza", "amount": 20.0, "category": "Food"}`

## Error Handling

- **Non-whitelisted users**: Returns access denied message
- **Invalid messages**: Returns helpful guidance
- **LLM parsing failures**: Falls back to regex-based extraction
- **Database errors**: Proper error logging and HTTP status codes

## Logging

Comprehensive logging includes:
- User whitelist checks
- Expense extraction results
- Database operations
- Error conditions with stack traces

## Development

### Running Tests
```bash
# Add your test commands here
pytest
```

### Code Style
```bash
# Format code
black .
flake8 .
```

## Deployment

### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
- Set `DATABASE_URL` to your production PostgreSQL instance
- Use a secure `OPENAI_API_KEY`
- Configure appropriate `BOT_SERVICE_HOST` and `BOT_SERVICE_PORT`

## Monitoring

The service provides:
- Health check endpoint at `/health`
- Comprehensive logging for monitoring
- Error tracking and reporting

## Security

- User whitelist validation prevents unauthorized access
- No sensitive data logged
- Proper error handling prevents information leakage 