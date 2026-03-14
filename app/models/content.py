"""Content-related database models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Source(Base):
    """Represents a PDF source document"""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(50), unique=True, index=True)  # e.g., SRC_001
    filename = Column(String(255), index=True)
    grade_level = Column(Integer)
    subject = Column(String(100), index=True)
    topic = Column(String(255), index=True)
    file_path = Column(String(500))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    content_summary = Column(Text, nullable=True)
    
    # Relationships
    chunks = relationship("ContentChunk", back_populates="source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Source {self.source_id}: {self.filename}>"


class ContentChunk(Base):
    """Represents a chunked segment of extracted content"""
    __tablename__ = "content_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String(50), unique=True, index=True)  # e.g., SRC_001_CH_01
    source_id = Column(Integer, ForeignKey("sources.id"), index=True)
    grade_level = Column(Integer)
    subject = Column(String(100), index=True)
    topic = Column(String(255), index=True)
    content_text = Column(Text)
    chunk_index = Column(Integer)  # Order of chunk within source
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    source = relationship("Source", back_populates="chunks")
    quiz_questions = relationship("QuizQuestion", back_populates="source_chunk")
    
    def __repr__(self):
        return f"<ContentChunk {self.chunk_id}>"
