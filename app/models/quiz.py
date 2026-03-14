"""Quiz and student interaction related database models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


class QuizQuestion(Base):
    """Represents a generated quiz question"""
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String(50), unique=True, index=True)  # e.g., Q12345
    source_chunk_id = Column(Integer, ForeignKey("content_chunks.id"), index=True)
    question_text = Column(Text)
    question_type = Column(String(20), index=True)  # MCQ, true_false, fill_blank
    options = Column(Text)  # JSON string of options
    correct_answer = Column(String(255))
    difficulty = Column(String(20), index=True)  # easy, medium, hard
    subject = Column(String(100), index=True)
    topic = Column(String(255), index=True)
    explanation = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    extra_metadata = Column(Text, nullable=True)  # JSON string for additional metadata
    
    # Relationships
    source_chunk = relationship("ContentChunk", back_populates="quiz_questions")
    student_answers = relationship("StudentAnswer", back_populates="question")
    
    def __repr__(self):
        return f"<QuizQuestion {self.question_id}>"


class StudentAnswer(Base):
    """Represents a student's answer to a quiz question"""
    __tablename__ = "student_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), index=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), index=True)
    selected_answer = Column(String(255))
    is_correct = Column(Boolean)
    time_spent_seconds = Column(Integer, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    question = relationship("QuizQuestion", back_populates="student_answers")
    
    def __repr__(self):
        return f"<StudentAnswer Student:{self.student_id} Question:{self.question_id}>"


class StudentProgress(Base):
    """Tracks student progress and adaptive difficulty"""
    __tablename__ = "student_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True)
    current_difficulty = Column(String(20), default="medium")  # easy, medium, hard
    total_questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    consecutive_correct = Column(Integer, default=0)
    consecutive_incorrect = Column(Integer, default=0)
    topics_covered = Column(Text, nullable=True)  # JSON list of topics
    last_activity = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @property
    def accuracy_percentage(self) -> float:
        """Calculate accuracy percentage"""
        if self.total_questions_answered == 0:
            return 0.0
        return (self.correct_answers / self.total_questions_answered) * 100
    
    def __repr__(self):
        return f"<StudentProgress Student:{self.student_id}>"
