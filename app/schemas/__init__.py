"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Content Schemas
class ContentChunkSchema(BaseModel):
    """Schema for content chunk response"""
    chunk_id: str
    subject: str
    topic: str
    grade_level: int
    content_text: str
    
    class Config:
        from_attributes = True


class SourceSchema(BaseModel):
    """Schema for source document response"""
    source_id: str
    filename: str
    subject: str
    topic: str
    grade_level: int
    uploaded_at: datetime
    chunks: List[ContentChunkSchema] = []
    
    class Config:
        from_attributes = True


# Quiz Schemas
class QuizQuestionSchema(BaseModel):
    """Schema for quiz question response (without answer/explanation)"""
    question_id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="The question text")
    question_type: str = Field(..., description="Type: MCQ, true_false, fill_blank")
    options: List[str] = Field(..., description="List of answer options")
    difficulty: str = Field(..., description="Difficulty level: easy, medium, hard")
    subject: str = Field(..., description="Subject of the question")
    topic: str = Field(..., description="Topic of the question")
    
    class Config:
        from_attributes = True


class QuizQuestionWithExplanationSchema(BaseModel):
    """Schema for quiz question with explanation (for answer reveal)"""
    question_id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="The question text")
    question_type: str = Field(..., description="Type: MCQ, true_false, fill_blank")
    options: List[str] = Field(..., description="List of answer options")
    difficulty: str = Field(..., description="Difficulty level: easy, medium, hard")
    subject: str = Field(..., description="Subject of the question")
    topic: str = Field(..., description="Topic of the question")
    explanation: Optional[str] = Field(None, description="Explanation for the answer")
    
    class Config:
        from_attributes = True


class QuizRequestSchema(BaseModel):
    """Schema for quiz request"""
    topic: Optional[str] = Field(None, description="Filter by topic")
    subject: Optional[str] = Field(None, description="Filter by subject")
    difficulty: Optional[str] = Field(None, description="Filter by difficulty")
    limit: int = Field(5, ge=1, le=50, description="Number of questions to return")
    student_id: Optional[str] = Field(None, description="Student ID for adaptive difficulty")


class StudentAnswerSubmissionSchema(BaseModel):
    """Schema for student answer submission"""
    student_id: str = Field(..., description="Student identifier")
    question_id: str = Field(..., description="Question identifier")
    selected_answer: str = Field(..., description="The answer selected by student")
    time_spent_seconds: Optional[int] = Field(None, description="Time spent on question")


class StudentAnswerResponseSchema(BaseModel):
    """Schema for student answer response"""
    is_correct: bool = Field(..., description="Whether answer is correct")
    correct_answer: str = Field(..., description="The correct answer")
    explanation: Optional[str] = Field(None, description="Question explanation")
    current_difficulty: str = Field(..., description="Updated difficulty level")
    accuracy_percentage: float = Field(..., description="Student accuracy percentage")
    
    class Config:
        from_attributes = True


class StudentProgressSchema(BaseModel):
    """Schema for student progress response"""
    student_id: str
    current_difficulty: str
    total_questions_answered: int
    correct_answers: int
    incorrect_answers: int
    accuracy_percentage: float
    consecutive_correct: int
    consecutive_incorrect: int
    last_activity: datetime
    
    class Config:
        from_attributes = True


# Ingestion Schemas
class IngestionResponseSchema(BaseModel):
    """Schema for PDF ingestion response"""
    source_id: str = Field(..., description="Generated source ID")
    filename: str = Field(..., description="Original filename")
    chunks_created: int = Field(..., description="Number of content chunks created")
    subject: str = Field(..., description="Extracted subject")
    topic: str = Field(..., description="Extracted topic")
    grade_level: int = Field(..., description="Extracted grade level")
    message: str = Field(..., description="Status message")


class QuizGenerationStatusSchema(BaseModel):
    """Schema for quiz generation status"""
    source_id: str = Field(..., description="Source document ID")
    total_chunks: int = Field(..., description="Total chunks in source")
    questions_generated: int = Field(..., description="Total questions generated")
    generation_time_seconds: float = Field(..., description="Time taken to generate")
    status: str = Field(..., description="Generation status: completed, in_progress, failed")
    message: str = Field(..., description="Status message")
