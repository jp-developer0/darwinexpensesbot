from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import OutputParserException
from pydantic import BaseModel, Field
from typing import Optional, Tuple
import re
import json
import logging
from config import settings

logger = logging.getLogger(__name__)


class ExpenseData(BaseModel):
    is_expense: bool = Field(description="Whether the message contains an expense")
    description: str = Field(description="Description of the expense")
    amount: float = Field(description="Numeric amount of the expense")
    category: str = Field(description="Category of the expense")


class ExpenseProcessor:
    CATEGORIES = [
        "Housing", "Transportation", "Food", "Utilities", "Insurance", 
        "Medical/Healthcare", "Savings", "Debt", "Education", "Entertainment", "Other"
    ]
    
    def __init__(self):
        self.llm = OpenAI(
            openai_api_key=settings.openai_api_key,
            temperature=0.1,
            model_name="gpt-3.5-turbo-instruct"
        )
        
        # Create the prompt template for expense analysis
        self.expense_prompt = PromptTemplate(
            input_variables=["message", "categories"],
            template="""
            Analyze the following message to determine if it contains an expense and extract relevant information.

            Categories available: {categories}

            Message: "{message}"

            Instructions:
            1. Determine if this message describes an expense (purchase, payment, cost, etc.)
            2. If it's an expense, extract:
               - Description: What was purchased/paid for
               - Amount: The numeric value (convert to decimal if needed)
               - Category: Choose the most appropriate category from the list

            Respond ONLY with a JSON object in this exact format:
            {{
                "is_expense": true/false,
                "description": "extracted description",
                "amount": numeric_value,
                "category": "selected_category"
            }}

            Examples:
            - "Pizza 20 bucks" → {{"is_expense": true, "description": "Pizza", "amount": 20.0, "category": "Food"}}
            - "Gas station $45" → {{"is_expense": true, "description": "Gas station", "amount": 45.0, "category": "Transportation"}}
            - "Hello how are you?" → {{"is_expense": false, "description": "", "amount": 0.0, "category": ""}}
            - "Rent payment 1200" → {{"is_expense": true, "description": "Rent payment", "amount": 1200.0, "category": "Housing"}}
            """
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.expense_prompt)

    def _extract_amount_fallback(self, text: str) -> Optional[float]:
        """Fallback method to extract amount using regex"""
        # Look for various currency patterns
        patterns = [
            r'\$(\d+(?:\.\d{2})?)',  # $20, $20.50
            r'(\d+(?:\.\d{2})?)(?:\s*(?:dollars?|bucks?|usd|\$))',  # 20 dollars, 20 bucks
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
        Process a message to extract expense information using LangChain
        
        Args:
            message: The user's message
            telegram_id: User's Telegram ID (for logging)
            
        Returns:
            ExpenseData if expense found, None otherwise
        """
        try:
            # Run LangChain analysis
            categories_str = ", ".join(self.CATEGORIES)
            result = await self.chain.arun(
                message=message.strip(),
                categories=categories_str
            )
            
            # Parse JSON response
            try:
                result_json = json.loads(result.strip())
            except json.JSONDecodeError:
                # Try to extract JSON from the response if it's wrapped in other text
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    result_json = json.loads(json_match.group())
                else:
                    raise
            
            # Validate the response
            if not result_json.get("is_expense", False):
                logger.info(f"Message not recognized as expense for user {telegram_id}: {message}")
                return None
            
            # Extract and validate data
            description = result_json.get("description", "").strip()
            amount = result_json.get("amount", 0)
            category = result_json.get("category", "Other").strip()
            
            # Fallback amount extraction if LLM failed
            if not amount or amount <= 0:
                amount = self._extract_amount_fallback(message)
                if not amount:
                    logger.warning(f"Could not extract amount from message: {message}")
                    return None
            
            # Validate category
            if category not in self.CATEGORIES:
                logger.warning(f"Invalid category '{category}', defaulting to 'Other'")
                category = "Other"
            
            # Use original message as description if extracted description is empty
            if not description:
                description = message.strip()
            
            expense_data = ExpenseData(
                is_expense=True,
                description=description,
                amount=amount,
                category=category
            )
            
            logger.info(f"Extracted expense for user {telegram_id}: {expense_data}")
            return expense_data
            
        except Exception as e:
            logger.error(f"Error processing message '{message}' for user {telegram_id}: {e}")
            
            # Try fallback processing
            try:
                amount = self._extract_amount_fallback(message)
                if amount and amount > 0:
                    logger.info(f"Using fallback processing for message: {message}")
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