from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from config import settings
from database import db
from expense_processor import expense_processor
from models import ProcessMessageRequest, ProcessMessageResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Bot Service...")
    await db.connect()
    logger.info("Bot Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bot Service...")
    await db.disconnect()
    logger.info("Bot Service shut down successfully")


# Create FastAPI application
app = FastAPI(
    title="Telegram Expense Bot Service",
    description="Python service for processing expense messages using LangChain",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "bot-service"}


@app.post("/process-message", response_model=ProcessMessageResponse)
async def process_message(request: ProcessMessageRequest):
    """
    Process a message from a Telegram user to extract and store expense information
    
    Args:
        request: ProcessMessageRequest containing message and telegram_id
        
    Returns:
        ProcessMessageResponse with success status and response message
    """
    try:
        # Check if user is whitelisted
        is_whitelisted = await db.is_user_whitelisted(request.telegram_id)
        if not is_whitelisted:
            logger.warning(f"Non-whitelisted user attempted to use bot: {request.telegram_id}")
            return ProcessMessageResponse(
                success=False,
                message="Access denied. You are not authorized to use this bot.",
                expense_added=False
            )
        
        # Get user from database
        user = await db.get_user_by_telegram_id(request.telegram_id)
        if not user:
            logger.error(f"User not found in database despite being whitelisted: {request.telegram_id}")
            raise HTTPException(status_code=500, detail="Internal server error")
        
        # Process the message to extract expense information
        expense_data = await expense_processor.process_message(request.message, request.telegram_id)
        
        if not expense_data:
            # Message is not an expense
            logger.info(f"Message from {request.telegram_id} not recognized as expense: {request.message}")
            return ProcessMessageResponse(
                success=True,
                message="I can help you track expenses. Send me messages like 'Pizza $20' or 'Gas station 45 dollars'.",
                expense_added=False
            )
        
        # Add expense to database
        expense_record = await db.add_expense(
            user_id=user["id"],
            description=expense_data.description,
            amount=expense_data.amount,
            category=expense_data.category
        )
        
        logger.info(f"Expense added successfully: {expense_record}")
        
        # Return success response
        return ProcessMessageResponse(
            success=True,
            message=f"{expense_data.category} expense added ✅",
            expense_added=True,
            category=expense_data.category
        )
        
    except Exception as e:
        logger.error(f"Error processing message from {request.telegram_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/add-user", response_model=dict)
async def add_user(telegram_id: str):
    """
    Add a new user to the whitelist
    
    Args:
        telegram_id: Telegram user ID to add
        
    Returns:
        Created user information
    """
    try:
        # Check if user already exists
        existing_user = await db.get_user_by_telegram_id(telegram_id)
        if existing_user:
            return {
                "message": "User already exists",
                "user": existing_user
            }
        
        # Create new user
        new_user = await db.create_user(telegram_id)
        logger.info(f"New user added to whitelist: {new_user}")
        
        return {
            "message": "User added successfully",
            "user": new_user
        }
        
    except Exception as e:
        logger.error(f"Error adding user {telegram_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add user: {str(e)}"
        )


@app.get("/users/{telegram_id}")
async def get_user(telegram_id: str):
    """
    Get user information by Telegram ID
    
    Args:
        telegram_id: Telegram user ID
        
    Returns:
        User information if found
    """
    try:
        user = await db.get_user_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"user": user}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {telegram_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.bot_service_host,
        port=settings.bot_service_port,
        reload=True,
        log_level="info"
    ) 