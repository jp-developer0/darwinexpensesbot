# Bot Service 🤖

The Python backend service that powers the expense categorization using **Google Gemini AI**.

## 🚀 Features

- **AI-Powered Analysis**: Uses Google Gemini 2.0 Flash for natural language understanding
- **Structured Output**: Reliable expense data extraction with Pydantic models
- **Smart Fallback**: Regex-based fallback when AI is unavailable
- **User Management**: Whitelist-based access control
- **Database Integration**: Async Supabase PostgreSQL operations
- **Production Ready**: FastAPI with proper logging and error handling

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│ Expense Processor │───▶│  Google Gemini  │
│                 │    │   (LangChain)    │    │       AI        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                                │
         ▼                                                ▼
┌─────────────────┐                            ┌─────────────────┐
│  Database Layer │                            │   Structured    │
│   (Supabase)    │◀───────────────────────────│     Output      │
└─────────────────┘                            └─────────────────┘
```

## 📁 Project Structure

```
bot-service/
├── main.py              # FastAPI application
├── expense_processor.py # AI-powered expense analysis
├── database.py          # Database operations
├── models.py            # Pydantic data models
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
└── Dockerfile          # Container configuration
```

## 🛠️ Development

### Local Setup

1. **Install Dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   export DATABASE_URL="postgresql://postgres:password@host:5432/postgres"
   export GOOGLE_API_KEY="your_google_api_key"
   export BOT_SERVICE_HOST="0.0.0.0"
   export BOT_SERVICE_PORT="8000"
   ```

3. **Run the Service**
   ```bash
   python main.py
   ```

### Docker

```bash
# Build image
docker build -t expense-bot-service .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="your_database_url" \
  -e GOOGLE_API_KEY="your_api_key" \
  expense-bot-service
```

## 📊 API Endpoints

### Health Check
```http
GET /health
```
Returns service status and version.

### Process Message
```http
POST /process-message
Content-Type: application/json

{
  "message": "Pizza $20",
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

### User Management
```http
# Add user to whitelist
POST /add-user?telegram_id=123456789

# Get user info
GET /users/123456789
```

## 🧠 AI Processing

### Google Gemini Integration

The service uses **Google Gemini 2.0 Flash** for expense analysis:

- **Model**: `gemini-2.0-flash-exp`
- **Temperature**: 0.1 (for consistent categorization)
- **Output**: Structured Pydantic models
- **Fallback**: Regex-based amount extraction

### Categories

| Category | Description |
|----------|-------------|
| **Food** | Restaurants, groceries, delivery |
| **Transportation** | Gas, car payments, public transport |
| **Housing** | Rent, mortgage, utilities |
| **Entertainment** | Movies, games, streaming |
| **Medical/Healthcare** | Doctor visits, medicine |
| **Education** | Tuition, books, courses |
| **Utilities** | Electricity, water, internet |
| **Insurance** | Health, car, home insurance |
| **Savings** | Investments, retirement |
| **Debt** | Loan payments, credit cards |
| **Other** | Miscellaneous expenses |

### Example Processing

```python
# Input: "Coffee at Starbucks $5.50"
# Output:
{
  "is_expense": true,
  "description": "Coffee at Starbucks",
  "amount": 5.50,
  "category": "Food"
}
```

## 🗄️ Database Operations

### Async Database Layer

- **Connection**: Async PostgreSQL with asyncpg
- **ORM**: Custom async database layer
- **SSL**: Configured for Supabase connections
- **Connection Pooling**: Efficient resource management

### Key Operations

```python
# User management
await db.create_user(telegram_id)
await db.get_user_by_telegram_id(telegram_id)
await db.is_user_whitelisted(telegram_id)

# Expense management
await db.add_expense(user_id, description, amount, category)
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Supabase PostgreSQL connection string | Required |
| `GOOGLE_API_KEY` | Google AI API key | Required |
| `BOT_SERVICE_HOST` | Service bind address | `0.0.0.0` |
| `BOT_SERVICE_PORT` | Service port | `8000` |

### SSL Configuration

For Supabase connections, SSL is automatically configured:
```python
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
```

## 🔍 Monitoring & Debugging

### Logging

The service provides comprehensive logging:
- **INFO**: Normal operations and successful processing
- **WARNING**: Fallback processing and validation issues
- **ERROR**: Failures and exceptions

### Health Monitoring

```bash
# Check service health
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "service": "bot-service",
  "version": "2.0.0"
}
```

## 🧪 Testing

### Manual Testing

```bash
# Add test user
curl -X POST "http://localhost:8000/add-user?telegram_id=123456789"

# Test expense processing
curl -X POST "http://localhost:8000/process-message" \
  -H "Content-Type: application/json" \
  -d '{"message": "Pizza $20", "telegram_id": "123456789"}'
```

### Expected Behavior

- ✅ "Pizza $20" → Food category
- ✅ "Gas station 45 dollars" → Transportation
- ✅ "Rent payment 1200" → Housing
- ❌ "Hello there" → Not an expense

## 🔧 Dependencies

### Core Dependencies

- **FastAPI**: Modern web framework
- **LangChain**: AI orchestration framework
- **Google Generative AI**: Gemini model integration
- **Pydantic**: Data validation and parsing
- **asyncpg**: Async PostgreSQL driver
- **uvicorn**: ASGI server

### Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Code formatting (optional)
pip install black isort
black .
isort .
```

---

**Built with Google Gemini AI and FastAPI** 🚀 