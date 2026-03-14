"""Configuration management for the application"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/quiz_engine"
    
    # LLM Configuration
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "gemini-pro"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2048
    
    # Application Settings
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # PDF Processing
    MAX_PDF_SIZE_MB: int = 50
    PDF_UPLOAD_DIR: str = "./pdfs"
    
    # Adaptive Difficulty
    INITIAL_DIFFICULTY: str = "medium"
    MAX_DIFFICULTY_INCREASE_PER_CORRECT: int = 1
    MAX_DIFFICULTY_DECREASE_PER_INCORRECT: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
