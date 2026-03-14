"""Content ingestion orchestration service"""
import logging
import os
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from app.services import PDFExtractionService
from app.services.quiz_generation import QuizGenerationService
from app.models.content import Source, ContentChunk
from app.models.quiz import QuizQuestion
from app.config import settings

logger = logging.getLogger(__name__)


class ContentIngestionService:
    """Service for orchestrating content ingestion from PDF files"""
    
    @staticmethod
    def ingest_pdf(
        db: Session,
        pdf_path: str,
        generate_quizzes: bool = True,
        questions_per_chunk: int = 3
    ) -> Dict:
        """
        Complete ingestion pipeline: Extract -> Clean -> Chunk -> Store -> Generate Quizzes
        
        Args:
            db: Database session
            pdf_path: Path to PDF file
            generate_quizzes: Whether to generate quiz questions
            questions_per_chunk: Number of questions per chunk
            
        Returns:
            Dictionary with ingestion results
        """
        
        filename = os.path.basename(pdf_path)
        logger.info(f"Starting ingestion of {filename}")
        
        try:
            # Step 1: Extract text from PDF
            raw_text = PDFExtractionService.extract_text_from_pdf(pdf_path)
            logger.info(f"Extracted {len(raw_text)} characters from PDF")
            
            # Step 2: Clean text
            cleaned_text = PDFExtractionService.clean_text(raw_text)
            logger.info(f"Cleaned text to {len(cleaned_text)} characters")
            
            # Step 3: Extract metadata from filename
            subject, grade_level, topic = PDFExtractionService.extract_metadata_from_filename(filename)
            logger.info(f"Extracted metadata: subject={subject}, grade={grade_level}, topic={topic}")
            
            # Step 4: Generate source ID
            source_id = PDFExtractionService.generate_source_id(filename)
            logger.info(f"Generated source_id: {source_id}")
            
            # Step 5: Create source record
            try:
                source = Source(
                    source_id=source_id,
                    filename=filename,
                    grade_level=grade_level,
                    subject=subject,
                    topic=topic,
                    file_path=pdf_path,
                    content_summary=cleaned_text[:500] if cleaned_text else "No content"
                )
                db.add(source)
                db.flush()  # Flush to get the ID without committing
                logger.info(f"Created source record with ID: {source.id}")
            except Exception as e:
                logger.error(f"Error creating source record: {e}")
                db.rollback()
                raise
            
            # Step 6: Chunk the content
            chunks = PDFExtractionService.chunk_text(cleaned_text)
            logger.info(f"Created {len(chunks)} chunks from PDF")
            
            # Step 7: Store chunks and generate questions
            chunk_records = []
            all_questions = []
            
            for chunk_index, chunk_text in enumerate(chunks):
                chunk_id = PDFExtractionService.generate_chunk_id(source_id, chunk_index)
                
                try:
                    # Create chunk record
                    chunk = ContentChunk(
                        chunk_id=chunk_id,
                        source_id=source.id,
                        grade_level=grade_level,
                        subject=subject,
                        topic=topic,
                        content_text=chunk_text,
                        chunk_index=chunk_index
                    )
                    db.add(chunk)
                    chunk_records.append({
                        'db_chunk': chunk,
                        'chunk_id': chunk_id,
                        'content': chunk_text,
                        'subject': subject,
                        'topic': topic,
                        'grade_level': grade_level
                    })
                except Exception as e:
                    logger.error(f"Error creating chunk {chunk_id}: {e}")
                    db.rollback()
                    raise
            
            db.flush()  # Flush chunks to database
            logger.info(f"Flushed {len(chunk_records)} chunks to database")
            
            # Step 8: Generate quiz questions
            if generate_quizzes:
                logger.info(f"Generating quiz questions for {source_id}")
                for record in chunk_records:
                    try:
                        questions = QuizGenerationService.generate_questions_for_chunk(
                            content_chunk=record['content'],
                            subject=subject,
                            topic=topic,
                            grade_level=grade_level,
                            chunk_id=record['chunk_id'],
                            num_questions=questions_per_chunk
                        )
                        
                        # Store questions in database
                        for q_idx, question in enumerate(questions):
                            # Create unique question ID
                            question_id = f"{source_id}_Q{len(all_questions):03d}"
                            
                            # Convert options to JSON string if it's a list
                            import json
                            options_json = json.dumps(question.get('options', []))
                            
                            try:
                                db_question = QuizQuestion(
                                    question_id=question_id,
                                    source_chunk_id=record['db_chunk'].id,
                                    question_text=question['question_text'],
                                    question_type=question['question_type'],
                                    options=options_json,
                                    correct_answer=question['correct_answer'],
                                    difficulty=question.get('difficulty', 'medium'),
                                    subject=question.get('subject', subject),
                                    topic=question.get('topic', topic),
                                    explanation=question.get('explanation', ''),
                                    extra_metadata=json.dumps({
                                        'grade_level': grade_level,
                                        'source_id': source_id
                                    })
                                )
                                db.add(db_question)
                                all_questions.append(question_id)
                            except Exception as e:
                                logger.error(f"Error creating question {question_id}: {e}")
                                db.rollback()
                                raise
                    except Exception as e:
                        logger.error(f"Error generating questions for chunk {record['chunk_id']}: {e}")
                        db.rollback()
                        raise
            
            db.commit()
            logger.info(f"Successfully committed ingestion to database")
            
            result = {
                "source_id": source_id,
                "filename": filename,
                "chunks_created": len(chunks),
                "subject": subject,
                "topic": topic,
                "grade_level": grade_level,
                "questions_generated": len(all_questions),
                "message": f"Successfully ingested {filename} with {len(chunks)} chunks and {len(all_questions)} questions"
            }
            
            logger.info(f"Ingestion completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error during ingestion: {e}", exc_info=True)
            db.rollback()
            raise
    
    @staticmethod
    def get_source_details(db: Session, source_id: str) -> Dict:
        """Get detailed information about an ingested source"""
        source = db.query(Source).filter(Source.source_id == source_id).first()
        
        if not source:
            return None
        
        chunks = db.query(ContentChunk).filter(ContentChunk.source_id == source.id).all()
        questions = db.query(QuizQuestion).filter(
            QuizQuestion.source_chunk_id.in_([c.id for c in chunks])
        ).all()
        
        return {
            "source_id": source.source_id,
            "filename": source.filename,
            "subject": source.subject,
            "topic": source.topic,
            "grade_level": source.grade_level,
            "chunks_count": len(chunks),
            "questions_count": len(questions),
            "uploaded_at": source.uploaded_at
        }
