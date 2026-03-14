"""PDF content extraction and processing service"""
import os
import re
from typing import List, Dict, Tuple
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)


class PDFExtractionService:
    """Service for extracting and processing PDF content"""
    
    # Grade level mapping from filename patterns
    GRADE_LEVEL_PATTERNS = {
        "grade1": 1,
        "grade2": 2,
        "grade3": 3,
        "grade4": 4,
        "grade5": 5,
        "grade6": 6,
        "grade7": 7,
        "grade8": 8,
        "grade9": 9,
        "grade10": 10,
        "grade11": 11,
        "grade12": 12,
    }
    
    # Subject mapping
    SUBJECT_PATTERNS = {
        "english": "English",
        "grammar": "English",
        "math": "Math",
        "science": "Science",
        "history": "History",
        "social": "Social Studies",
    }
    
    CHUNK_SIZE = 500  # Approximate characters per chunk
    OVERLAP = 100  # Character overlap between chunks
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Extract raw text from PDF file"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            reader = PdfReader(pdf_path)
            extracted_text = ""
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                extracted_text += text + "\n"
            
            logger.info(f"Extracted {len(extracted_text)} characters from {pdf_path}")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep essential punctuation
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Fix common OCR issues
        text = re.sub(r'(\w)\s([.!?])', r'\1\2', text)
        
        return text.strip()
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
        """
        Break text into manageable chunks with overlap to maintain context
        
        Args:
            text: Text to chunk
            chunk_size: Target size of each chunk in characters
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of text chunks
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # Create overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else ""
                current_chunk = overlap_text + sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if len(chunk) > 50]  # Filter very short chunks
    
    @staticmethod
    def extract_metadata_from_filename(filename: str) -> Tuple[str, int, str]:
        """
        Extract subject, grade level, and topic from filename
        
        Format example: peblo_pdf_grade4_english_grammar.pdf
        
        Returns:
            Tuple of (subject, grade_level, topic)
        """
        filename_lower = filename.lower()
        
        # Extract grade level
        grade_level = 1  # Default
        for pattern, level in PDFExtractionService.GRADE_LEVEL_PATTERNS.items():
            if pattern in filename_lower:
                grade_level = level
                break
        
        # Extract subject
        subject = "Other"
        for pattern, subj in PDFExtractionService.SUBJECT_PATTERNS.items():
            if pattern in filename_lower:
                subject = subj
                break
        
        # Extract topic (remaining word after subject/grade)
        words = filename_lower.replace('.pdf', '').replace('_', ' ').split()
        topic_words = [w for w in words if w not in 
                      list(PDFExtractionService.GRADE_LEVEL_PATTERNS.keys()) +
                      list(PDFExtractionService.SUBJECT_PATTERNS.keys()) +
                      ['peblo', 'pdf']]
        topic = ' '.join(topic_words).title() if topic_words else subject
        
        return subject, grade_level, topic
    
    @staticmethod
    def generate_source_id(filename: str) -> str:
        """Generate a unique source ID"""
        # Use simplified version of filename as base
        base = filename.replace('.pdf', '').replace('_', '')[:20]
        import hashlib
        hash_suffix = hashlib.md5(filename.encode()).hexdigest()[:8].upper()
        return f"SRC_{hash_suffix}"
    
    @staticmethod
    def generate_chunk_id(source_id: str, chunk_index: int) -> str:
        """Generate chunk ID"""
        return f"{source_id}_CH_{chunk_index:02d}"
