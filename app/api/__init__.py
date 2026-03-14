"""API routes initialization"""
from app.api.ingestion import router as ingestion_router
from app.api.quiz import router as quiz_router
from app.api.test import router as test_router

__all__ = ["ingestion_router", "quiz_router", "test_router"]
