from pydantic import BaseModel, Field
from typing import Optional


class ProcessMessageRequest(BaseModel):
    message: str = Field(description="The message text to process")
    telegram_id: str = Field(description="Telegram user ID")


class ProcessMessageResponse(BaseModel):
    success: bool = Field(description="Whether the message was processed successfully")
    message: str = Field(description="Response message to send back to user")
    expense_added: bool = Field(description="Whether an expense was added")
    category: Optional[str] = Field(default=None, description="Category of the added expense")


class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information") 