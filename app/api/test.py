"""Test/Demo API endpoints for database population"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.content import Source, ContentChunk
from app.models.quiz import QuizQuestion

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/test", tags=["test"])


@router.post("/populate-demo-data")
async def populate_demo_data(db: Session = Depends(get_db)):
    """
    Populate database with demo data for testing
    This is useful for testing without needing to upload a PDF
    """
    
    try:
        # Clear existing data
        db.query(QuizQuestion).delete()
        db.query(ContentChunk).delete()
        db.query(Source).delete()
        db.commit()
        logger.info("Cleared existing data")
        
        # Create source document
        source = Source(
            source_id="DEMO_SRC_001",
            filename="demo_grammar.pdf",
            grade_level=4,
            subject="English",
            topic="Grammar",
            file_path="./pdfs/demo_grammar.pdf",
            content_summary="Demo content for testing"
        )
        db.add(source)
        db.flush()
        logger.info("Created source: DEMO_SRC_001")
        
        # Create content chunk
        chunk = ContentChunk(
            chunk_id="DEMO_SRC_001_CH_00",
            source_id=source.id,
            grade_level=4,
            subject="English",
            topic="Grammar",
            content_text="This is demo content about grammar",
            chunk_index=0
        )
        db.add(chunk)
        db.flush()
        logger.info("Created chunk: DEMO_SRC_001_CH_00")
        
        # Create demo questions
        demo_questions = [
            {
                "question_id": "DEMO_SRC_001_Q000",
                "question_text": "What is a noun?",
                "question_type": "MCQ",
                "options": '["A word that names a person, place, or thing", "An action", "A feeling", "A color"]',
                "correct_answer": "A word that names a person, place, or thing",
                "difficulty": "easy",
                "explanation": "A noun is a part of speech that names a person, place, or thing."
            },
            {
                "question_id": "DEMO_SRC_001_Q001",
                "question_text": "Adjectives describe nouns.",
                "question_type": "true_false",
                "options": '["True", "False"]',
                "correct_answer": "True",
                "difficulty": "easy",
                "explanation": "True. Adjectives are words that modify or describe nouns."
            },
            {
                "question_id": "DEMO_SRC_001_Q002",
                "question_text": "The opposite of 'hot' is ____.",
                "question_type": "fill_blank",
                "options": '[]',
                "correct_answer": "cold",
                "difficulty": "medium",
                "explanation": "Cold is the opposite of hot."
            },
            {
                "question_id": "DEMO_SRC_001_Q003",
                "question_text": "Which of the following is a verb?",
                "question_type": "MCQ",
                "options": '["Run", "Happy", "Table", "Quickly"]',
                "correct_answer": "Run",
                "difficulty": "medium",
                "explanation": "Run is an action verb. Happy is an adjective, table is a noun, and quickly is an adverb."
            },
            {
                "question_id": "DEMO_SRC_001_Q004",
                "question_text": "Pronouns replace nouns in sentences.",
                "question_type": "true_false",
                "options": '["True", "False"]',
                "correct_answer": "True",
                "difficulty": "hard",
                "explanation": "True. Pronouns like he, she, it, they replace nouns in sentences."
            }
        ]
        
        for q_data in demo_questions:
            question = QuizQuestion(
                question_id=q_data["question_id"],
                source_chunk_id=chunk.id,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                difficulty=q_data["difficulty"],
                subject="English",
                topic="Grammar",
                explanation=q_data["explanation"],
                extra_metadata='{"demo": true}'
            )
            db.add(question)
            logger.info(f"Created question: {q_data['question_id']}")
        
        db.commit()
        logger.info("Successfully populated demo data")
        
        return {
            "status": "success",
            "message": "Demo data populated successfully",
            "source_id": "DEMO_SRC_001",
            "chunks_created": 1,
            "questions_created": len(demo_questions),
            "note": "Run GET /api/quiz to see the questions"
        }
        
    except Exception as e:
        logger.error(f"Error populating demo data: {e}", exc_info=True)
        db.rollback()
        raise


@router.get("/check-database")
async def check_database(db: Session = Depends(get_db)):
    """Check what's in the database"""
    
    sources = db.query(Source).count()
    chunks = db.query(ContentChunk).count()
    questions = db.query(QuizQuestion).count()
    
    return {
        "sources": sources,
        "chunks": chunks,
        "questions": questions,
        "message": "Use POST /api/test/populate-demo-data to add demo data"
    }
