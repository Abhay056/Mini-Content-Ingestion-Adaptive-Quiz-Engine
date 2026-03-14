"""Database and application initialization utilities"""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_directories():
    """Ensure required directories exist"""
    directories = [
        './pdfs',
        './logs',
        './uploads'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")


def initialize_application():
    """Initialize application on startup"""
    # Ensure directories exist
    ensure_directories()
    
    # Initialize database
    from app.database import init_db
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


if __name__ == "__main__":
    initialize_application()
