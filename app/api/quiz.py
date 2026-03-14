"""API routes for quiz operations"""
import json
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    QuizQuestionSchema,
    QuizRequestSchema,
    StudentAnswerSubmissionSchema,
    StudentAnswerResponseSchema,
    StudentProgressSchema
)
from app.models.quiz import QuizQuestion, StudentAnswer, StudentProgress
from app.services.adaptive_difficulty import AdaptiveDifficultyService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["quiz"])


@router.get("/quiz", response_model=List[QuizQuestionSchema])
async def get_quiz(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    limit: int = Query(5, ge=1, le=50, description="Number of questions"),
    student_id: Optional[str] = Query(None, description="Student ID for adaptive difficulty"),
    db: Session = Depends(get_db)
) -> List[QuizQuestionSchema]:
    """
    Get quiz questions with optional filters
    
    - **topic**: Filter by topic (optional)
    - **subject**: Filter by subject (optional)
    - **difficulty**: Filter by difficulty: easy, medium, hard (optional)
    - **limit**: Number of questions to return (1-50, default: 5)
    - **student_id**: Student ID for adaptive difficulty selection (optional)
    """
    
    try:
        questions = AdaptiveDifficultyService.select_quiz_questions(
            db=db,
            limit=limit,
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            student_id=student_id
        )
        
        if not questions:
            raise HTTPException(status_code=404, detail="No questions found matching criteria")
        
        # Convert questions to response schema
        response = []
        for q in questions:
            options = json.loads(q.options) if q.options else []
            response.append(QuizQuestionSchema(
                question_id=q.question_id,
                question_text=q.question_text,
                question_type=q.question_type,
                options=options,
                difficulty=q.difficulty,
                subject=q.subject,
                topic=q.topic,
                explanation=q.explanation
            ))
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quiz questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-answer", response_model=StudentAnswerResponseSchema)
async def submit_answer(
    submission: StudentAnswerSubmissionSchema,
    db: Session = Depends(get_db)
) -> StudentAnswerResponseSchema:
    """
    Submit a student answer and get evaluation
    
    Request body:
    - **student_id**: Student identifier
    - **question_id**: Question identifier
    - **selected_answer**: The answer selected by student
    - **time_spent_seconds**: Time spent on question (optional)
    """
    
    try:
        # Find the question
        question = db.query(QuizQuestion).filter(
            QuizQuestion.question_id == submission.question_id
        ).first()
        
        if not question:
            raise HTTPException(status_code=404, detail=f"Question {submission.question_id} not found")
        
        # Check if answer is correct
        is_correct = submission.selected_answer.strip().lower() == question.correct_answer.strip().lower()
        
        # Store the answer
        student_answer = StudentAnswer(
            student_id=submission.student_id,
            question_id=question.id,
            selected_answer=submission.selected_answer,
            is_correct=is_correct,
            time_spent_seconds=submission.time_spent_seconds
        )
        db.add(student_answer)
        
        # Update adaptive difficulty
        new_difficulty = AdaptiveDifficultyService.update_difficulty_after_answer(
            db=db,
            student_id=submission.student_id,
            is_correct=is_correct
        )
        
        # Get updated progress for accuracy
        progress = AdaptiveDifficultyService.get_or_create_student_progress(
            db=db,
            student_id=submission.student_id
        )
        
        db.commit()
        
        response = StudentAnswerResponseSchema(
            is_correct=is_correct,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            current_difficulty=new_difficulty,
            accuracy_percentage=progress.accuracy_percentage
        )
        
        logger.info(
            f"Answer submitted: Student={submission.student_id}, "
            f"Question={submission.question_id}, Correct={is_correct}"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/student-progress/{student_id}", response_model=StudentProgressSchema)
async def get_student_progress(
    student_id: str,
    db: Session = Depends(get_db)
) -> StudentProgressSchema:
    """
    Get student progress and adaptive difficulty information
    
    - **student_id**: Student identifier
    """
    
    try:
        progress = AdaptiveDifficultyService.get_or_create_student_progress(
            db=db,
            student_id=student_id
        )
        
        return StudentProgressSchema(
            student_id=progress.student_id,
            current_difficulty=progress.current_difficulty,
            total_questions_answered=progress.total_questions_answered,
            correct_answers=progress.correct_answers,
            incorrect_answers=progress.incorrect_answers,
            accuracy_percentage=progress.accuracy_percentage,
            consecutive_correct=progress.consecutive_correct,
            consecutive_incorrect=progress.consecutive_incorrect,
            last_activity=progress.last_activity
        )
        
    except Exception as e:
        logger.error(f"Error fetching student progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quiz/by-subject/{subject}")
async def get_quiz_by_subject(
    subject: str,
    difficulty: Optional[str] = Query(None),
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db)
) -> List[QuizQuestionSchema]:
    """
    Get quiz questions filtered by subject
    
    - **subject**: Subject name
    - **difficulty**: Optional difficulty filter
    - **limit**: Number of questions to return
    """
    
    return await get_quiz(
        subject=subject,
        difficulty=difficulty,
        limit=limit,
        db=db
    )


@router.get("/quiz/by-topic/{topic}")
async def get_quiz_by_topic(
    topic: str,
    difficulty: Optional[str] = Query(None),
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db)
) -> List[QuizQuestionSchema]:
    """
    Get quiz questions filtered by topic
    
    - **topic**: Topic name
    - **difficulty**: Optional difficulty filter
    - **limit**: Number of questions to return
    """
    
    return await get_quiz(
        topic=topic,
        difficulty=difficulty,
        limit=limit,
        db=db
    )
