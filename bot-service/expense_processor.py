"""
Expense Processing Module

This module handles the AI-powered analysis and categorization of expense messages
using Google Gemini AI with structured output parsing.
"""

import os
import re
import logging
from typing import Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Literal

from config import settings

logger = logging.getLogger(__name__)


class ExpenseData(BaseModel):
    """Data model for parsed expense information."""
    
    is_expense: bool = Field(description="Whether the message contains an expense")
    description: str = Field(description="Clean description of what was purchased/paid for")
    amount: float = Field(description="Numeric amount of the expense")
    category: Literal[
        "Housing", "Transportation", "Food", "Utilities", "Insurance",
        "Medical/Healthcare", "Savings", "Debt", "Education", "Entertainment", "Other"
    ] = Field(description="Most appropriate category for this expense")


class ExpenseProcessor:
    """
    Processes natural language messages to extract and categorize expense information
    using Google Gemini AI.
    """
    
    # Supported expense categories
    CATEGORIES: List[str] = [
        "Housing", "Transportation", "Food", "Utilities", "Insurance", 
        "Medical/Healthcare", "Savings", "Debt", "Education", "Entertainment", "Other"
    ]
    
    # Category examples for better AI understanding
    CATEGORY_EXAMPLES = {
        "Housing": "rent, mortgage, utilities, home maintenance, furniture",
        "Transportation": "gas, car payments, public transport, taxi, parking",
        "Food": "restaurants, groceries, coffee, delivery, snacks",
        "Utilities": "electricity, water, internet, phone bills",
        "Insurance": "health, car, home, life insurance",
        "Medical/Healthcare": "doctor visits, medicine, dental, health services",
        "Savings": "investments, savings accounts, retirement contributions",
        "Debt": "loan payments, credit card payments",
        "Education": "tuition, books, courses, training",
        "Entertainment": "movies, games, concerts, streaming services, hobbies",
        "Other": "anything that doesn't fit the above categories"
    }
    
    def __init__(self) -> None:
        """Initialize the expense processor with Google Gemini AI."""
        self._setup_ai_model()
        self._setup_prompt_template()
        self._create_processing_chain()

    def _setup_ai_model(self) -> None:
        """Initialize the Google Gemini AI model."""
        os.environ["GOOGLE_API_KEY"] = settings.google_api_key
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                google_api_key=settings.google_api_key,
                temperature=0.1,
                convert_system_message_to_human=True
            )
            logger.info("Successfully initialized Google Gemini model")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise

    def _setup_prompt_template(self) -> None:
        """Set up the prompt template for expense analysis."""
        # Set up the parser for structured output
        self.parser = PydanticOutputParser(pydantic_object=ExpenseData)
        
        # Create category descriptions
        category_list = "\n".join([
            f"- {cat}: {self.CATEGORY_EXAMPLES[cat]}" 
            for cat in self.CATEGORIES
        ])
        
        # Create the chat prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", f"""You are an expert expense categorization assistant. Analyze messages to determine if they contain expense information and categorize them appropriately.

Available categories:
{category_list}

Instructions:
1. Determine if the message describes an expense (purchase, payment, cost)
2. Extract a clean description of what was purchased/paid for
3. Extract the numeric amount (convert words like "twenty" to numbers)
4. Choose the most appropriate category

Examples:
- "Pizza 20 bucks" → Food category, amount: 20.0, description: "Pizza"
- "Gas station $45" → Transportation category, amount: 45.0, description: "Gas"
- "Rent payment 1200" → Housing category, amount: 1200.0, description: "Rent payment"
- "Coffee at Starbucks 5.50" → Food category, amount: 5.50, description: "Coffee at Starbucks"

{{format_instructions}}

Now analyze this message: {{message}}""")
        ])
        
        # Add format instructions to the prompt
        self.prompt = self.prompt.partial(format_instructions=self.parser.get_format_instructions())

    def _create_processing_chain(self) -> None:
        """Create the LangChain processing chain."""
        self.chain = self.prompt | self.llm | self.parser

    def _extract_amount_fallback(self, text: str) -> Optional[float]:
        """
        Fallback method to extract amount using regex patterns.
        
        Args:
            text: Input text to search for amounts
            
        Returns:
            Extracted amount or None if not found
        """
        patterns = [
            r'\$(\d+(?:\.\d{2})?)',  # $20, $20.50
            r'(\d+(?:\.\d{2})?)(?:\s*(?:dollars?|bucks?|usd|\$))',  # 20 dollars, 20 bucks
            r'(\d+(?:\.\d{2})?)(?:\s*(?:pesos?|euros?|pounds?))',  # 20 pesos, 80 pesos
            r'(\d+(?:\.\d{2})?)',  # Just numbers
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None

    async def process_message(self, message: str, telegram_id: str) -> Optional[ExpenseData]:
        """
        Process a message to extract expense information using Google Gemini.
        
        Args:
            message: The user's message to analyze
            telegram_id: User's Telegram ID (for logging purposes)
            
        Returns:
            ExpenseData if expense found and valid, None otherwise
        """
        if not message or not message.strip():
            logger.warning(f"Empty message received from user {telegram_id}")
            return None
            
        try:
            # Use Gemini AI to analyze the message
            logger.info(f"Processing message with Gemini: '{message}' for user {telegram_id}")
            
            result = await self.chain.ainvoke({"message": message.strip()})
            
            # Check if message contains an expense
            if not result.is_expense:
                logger.info(f"Message not recognized as expense for user {telegram_id}: {message}")
                return None
            
            # Validate and fix amount if needed
            if not result.amount or result.amount <= 0:
                logger.warning(f"Invalid amount extracted: {result.amount}, trying fallback")
                fallback_amount = self._extract_amount_fallback(message)
                if fallback_amount and fallback_amount > 0:
                    result.amount = fallback_amount
                else:
                    logger.warning(f"Could not extract valid amount from message: {message}")
                    return None
            
            # Ensure description is not empty
            if not result.description.strip():
                result.description = message.strip()
            
            # Validate category
            if result.category not in self.CATEGORIES:
                logger.warning(f"Invalid category '{result.category}', defaulting to 'Other'")
                result.category = "Other"
            
            logger.info(f"Successfully extracted expense for user {telegram_id}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing message '{message}' for user {telegram_id}: {e}")
            return self._fallback_processing(message, telegram_id)

    def _fallback_processing(self, message: str, telegram_id: str) -> Optional[ExpenseData]:
        """
        Basic fallback processing when AI fails.
        
        Args:
            message: Original message text
            telegram_id: User's Telegram ID
            
        Returns:
            Basic ExpenseData or None if fallback also fails
        """
        try:
            amount = self._extract_amount_fallback(message)
            if amount and amount > 0:
                logger.info(f"Using basic fallback processing for message: {message}")
                return ExpenseData(
                    is_expense=True,
                    description=message.strip(),
                    amount=amount,
                    category="Other"
                )
        except Exception as fallback_error:
            logger.error(f"Fallback processing also failed: {fallback_error}")
        
        return None


# Global expense processor instance
expense_processor = ExpenseProcessor() 