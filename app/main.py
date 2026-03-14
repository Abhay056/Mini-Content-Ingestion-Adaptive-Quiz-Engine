"""Main FastAPI application"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import ingestion_router, quiz_router, test_router
from app.config import settings

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Initializing database...")
    init_db()
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown")


# Create FastAPI application
app = FastAPI(
    title="Mini Content Ingestion and Adaptive Quiz Engine",
    description="API for PDF ingestion, quiz generation, and adaptive learning",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingestion_router)
app.include_router(quiz_router)
app.include_router(test_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mini Content Ingestion and Adaptive Quiz Engine",
        "version": "1.0.0",
        "status": "operational",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "Quiz Engine",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.LOG_LEVEL.lower()
    )
