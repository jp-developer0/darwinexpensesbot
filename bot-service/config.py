from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    database_url: str
    
    # OpenAI Configuration
    openai_api_key: str
    
    # Service Configuration
    bot_service_host: str = "0.0.0.0"
    bot_service_port: int = 8000
    
    # Optional: Alternative LLM providers
    anthropic_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 