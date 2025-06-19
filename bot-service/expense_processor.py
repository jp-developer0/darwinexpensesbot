import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional, Literal
import re
import logging
from config import settings

logger = logging.getLogger(__name__)


class ExpenseData(BaseModel):
    is_expense: bool = Field(description="Whether the message contains an expense")
    description: str = Field(description="Clean description of what was purchased/paid for")
    amount: float = Field(description="Numeric amount of the expense")
    category: Literal[
        "Housing", "Transportation", "Food", "Utilities", "Insurance",
        "Medical/Healthcare", "Savings", "Debt", "Education", "Entertainment", "Other"
    ] = Field(description="Most appropriate category for this expense")


class ExpenseProcessor:
    CATEGORIES = [
        "Housing", "Transportation", "Food", "Utilities", "Insurance", 
        "Medical/Healthcare", "Savings", "Debt", "Education", "Entertainment", "Other"
    ]
    
    def __init__(self):
        # Set up Google API key
        os.environ["GOOGLE_API_KEY"] = settings.google_api_key
        
        # Initialize the Gemini model with system message conversion
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
        
        # Set up the parser for structured output
        self.parser = PydanticOutputParser(pydantic_object=ExpenseData)
        
        # Create the chat prompt template using only human messages
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", """You are an expert expense categorization assistant. Analyze messages to determine if they contain expense information and categorize them appropriately.

Available categories:
- Housing: rent, mortgage, utilities, home maintenance, furniture
- Transportation: gas, car payments, public transport, taxi, parking
- Food: restaurants, groceries, coffee, delivery, snacks
- Utilities: electricity, water, internet, phone bills
- Insurance: health, car, home, life insurance
- Medical/Healthcare: doctor visits, medicine, dental, health services
- Savings: investments, savings accounts, retirement contributions
- Debt: loan payments, credit card payments
- Education: tuition, books, courses, training
- Entertainment: movies, games, concerts, streaming services, hobbies
- Other: anything that doesn't fit the above categories

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

{format_instructions}

Now analyze this message: {message}""")
        ])
        
        # Add format instructions to the prompt
        self.prompt = self.prompt.partial(format_instructions=self.parser.get_format_instructions())
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.parser

    def _extract_amount_fallback(self, text: str) -> Optional[float]:
        """Fallback method to extract amount using regex"""
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
        Process a message to extract expense information using Google Gemini
        
        Args:
            message: The user's message
            telegram_id: User's Telegram ID (for logging)
            
        Returns:
            ExpenseData if expense found, None otherwise
        """
        try:
            # Use Gemini to analyze the message
            logger.info(f"Processing message with Gemini: '{message}' for user {telegram_id}")
            
            result = await self.chain.ainvoke({"message": message.strip()})
            
            # Validate the result
            if not result.is_expense:
                logger.info(f"Message not recognized as expense for user {telegram_id}: {message}")
                return None
            
            # Validate amount
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
            
            # Try basic fallback processing
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