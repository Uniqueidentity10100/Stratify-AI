"""
Configuration management for Stratify AI
Loads environment variables and provides application settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional, List, Union


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    All secrets must be stored in .env file, never hardcoded
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_parse_none_str='',  # Parse empty strings as None
    )
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/stratify_db"
    
    # JWT Authentication Settings
    SECRET_KEY: str  # Must be provided in .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # API Keys - All required for functionality
    COINGECKO_API_KEY: Optional[str] = None  # Free tier doesn't require key
    FRED_API_KEY: str  # Required - get from https://fred.stlouisfed.org/
    NEWS_API_KEY: str  # Required - get from https://newsapi.org/
    
    # Ollama Settings (local open-source LLM)
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"  # Ollama OpenAI-compatible endpoint
    OLLAMA_MODEL: str = "llama3.1:8b"  # Default model, change to any pulled model
    
    # Application Settings
    APP_NAME: str = "Stratify AI"
    DEBUG: bool = False
    
    # CORS Settings - stored as comma-separated string in .env
    ALLOWED_ORIGINS: Union[List[str], str] = "http://localhost:3000,http://localhost:5173"
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_origins(cls, v):
        """Convert comma-separated string to list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v


# Create global settings instance
settings = Settings()
