"""API routes for content ingestion"""
import logging
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.schemas import IngestionResponseSchema, QuizGenerationStatusSchema
from app.services.ingestion import ContentIngestionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ingestion"])


@router.post("/ingest", response_model=IngestionResponseSchema)
async def ingest_pdf(
    file: UploadFile = File(...),
    generate_quizzes: bool = True,
    questions_per_chunk: int = 3,
    db: Session = Depends(get_db)
):
    """
    Ingest a PDF file and extract content
    
    - **file**: PDF file to ingest
    - **generate_quizzes**: Whether to generate quiz questions (default: true)
    - **questions_per_chunk**: Number of questions per chunk (default: 3)
    """
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Validate file size
    file_size_mb = file.size / (1024 * 1024) if file.size else 0
    if file_size_mb > settings.MAX_PDF_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds {settings.MAX_PDF_SIZE_MB}MB limit"
        )
    
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs(settings.PDF_UPLOAD_DIR, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(settings.PDF_UPLOAD_DIR, file.filename)
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        logger.info(f"Uploaded PDF: {file.filename} to {file_path}")
        
        # Perform ingestion
        result = ContentIngestionService.ingest_pdf(
            db=db,
            pdf_path=file_path,
            generate_quizzes=generate_quizzes,
            questions_per_chunk=questions_per_chunk
        )
        
        return IngestionResponseSchema(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during PDF ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingest/status/{source_id}", response_model=QuizGenerationStatusSchema)
async def get_ingestion_status(
    source_id: str,
    db: Session = Depends(get_db)
):
    """
    Get status of PDF ingestion and quiz generation
    
    - **source_id**: The source document ID to check status for
    """
    
    try:
        details = ContentIngestionService.get_source_details(db, source_id)
        
        if not details:
            raise HTTPException(status_code=404, detail=f"Source {source_id} not found")
        
        return QuizGenerationStatusSchema(
            source_id=source_id,
            total_chunks=details['chunks_count'],
            questions_generated=details['questions_count'],
            generation_time_seconds=0,  # Could be enhanced with actual timing
            status="completed",
            message="Ingestion and quiz generation completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ingestion status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
