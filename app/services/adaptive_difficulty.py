"""Adaptive difficulty and quiz selection logic"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.quiz import StudentProgress, QuizQuestion
from app.config import settings

logger = logging.getLogger(__name__)


class AdaptiveDifficultyService:
    """Service for managing adaptive difficulty based on student performance"""
    
    DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
    DIFFICULTY_INDEX = {"easy": 0, "medium": 1, "hard": 2}
    
    @staticmethod
    def get_or_create_student_progress(db: Session, student_id: str) -> StudentProgress:
        """Get existing student progress or create new one"""
        progress = db.query(StudentProgress).filter(
            StudentProgress.student_id == student_id
        ).first()
        
        if not progress:
            progress = StudentProgress(
                student_id=student_id,
                current_difficulty=settings.INITIAL_DIFFICULTY
            )
            db.add(progress)
            db.commit()
            logger.info(f"Created new student progress for {student_id}")
        
        return progress
    
    @staticmethod
    def update_difficulty_after_answer(
        db: Session,
        student_id: str,
        is_correct: bool
    ) -> str:
        """
        Update student difficulty based on answer correctness
        
        Algorithm:
        - Correct answer: increase difficulty (up to hard)
        - Incorrect answer: decrease difficulty (down to easy)
        - Track consecutive correct/incorrect for better adaptation
        
        Returns:
            New difficulty level
        """
        progress = AdaptiveDifficultyService.get_or_create_student_progress(db, student_id)
        
        # Update answer counts
        progress.total_questions_answered += 1
        
        if is_correct:
            progress.correct_answers += 1
            progress.consecutive_correct += 1
            progress.consecutive_incorrect = 0
            
            # Increase difficulty on 2 consecutive correct answers
            if progress.consecutive_correct >= 2:
                current_idx = AdaptiveDifficultyService.DIFFICULTY_INDEX[progress.current_difficulty]
                if current_idx < len(AdaptiveDifficultyService.DIFFICULTY_LEVELS) - 1:
                    new_idx = min(
                        current_idx + settings.MAX_DIFFICULTY_INCREASE_PER_CORRECT,
                        len(AdaptiveDifficultyService.DIFFICULTY_LEVELS) - 1
                    )
                    progress.current_difficulty = AdaptiveDifficultyService.DIFFICULTY_LEVELS[new_idx]
                    progress.consecutive_correct = 0
                    logger.info(f"Increased difficulty for {student_id} to {progress.current_difficulty}")
        
        else:
            progress.incorrect_answers += 1
            progress.consecutive_incorrect += 1
            progress.consecutive_correct = 0
            
            # Decrease difficulty on 2 consecutive incorrect answers
            if progress.consecutive_incorrect >= 2:
                current_idx = AdaptiveDifficultyService.DIFFICULTY_INDEX[progress.current_difficulty]
                if current_idx > 0:
                    new_idx = max(
                        current_idx - settings.MAX_DIFFICULTY_DECREASE_PER_INCORRECT,
                        0
                    )
                    progress.current_difficulty = AdaptiveDifficultyService.DIFFICULTY_LEVELS[new_idx]
                    progress.consecutive_incorrect = 0
                    logger.info(f"Decreased difficulty for {student_id} to {progress.current_difficulty}")
        
        db.commit()
        return progress.current_difficulty
    
    @staticmethod
    def get_recommended_difficulty(db: Session, student_id: str) -> str:
        """Get recommended difficulty for a student based on performance"""
        progress = AdaptiveDifficultyService.get_or_create_student_progress(db, student_id)
        
        # Dynamic recommendation based on accuracy
        accuracy = progress.accuracy_percentage
        
        if accuracy >= 80:
            return "hard"
        elif accuracy >= 60:
            return "medium"
        else:
            return "easy"
    
    @staticmethod
    def select_quiz_questions(
        db: Session,
        limit: int = 5,
        topic: Optional[str] = None,
        subject: Optional[str] = None,
        difficulty: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> List[QuizQuestion]:
        """
        Select quiz questions with optional adaptive difficulty
        
        Args:
            db: Database session
            limit: Number of questions to return
            topic: Filter by topic
            subject: Filter by subject
            difficulty: Specific difficulty (overrides adaptive)
            student_id: For adaptive difficulty selection
            
        Returns:
            List of selected questions
        """
        query = db.query(QuizQuestion)
        
        # Apply filters
        if topic:
            query = query.filter(QuizQuestion.topic == topic)
        
        if subject:
            query = query.filter(QuizQuestion.subject == subject)
        
        # Determine difficulty
        if not difficulty and student_id:
            # Use adaptive difficulty
            progress = AdaptiveDifficultyService.get_or_create_student_progress(
                db, student_id
            )
            difficulty = progress.current_difficulty
        elif not difficulty:
            difficulty = settings.INITIAL_DIFFICULTY
        
        query = query.filter(QuizQuestion.difficulty == difficulty)
        
        # Get questions
        questions = query.limit(limit).all()
        
        logger.info(f"Selected {len(questions)} questions for difficulty={difficulty}")
        
        return questions
