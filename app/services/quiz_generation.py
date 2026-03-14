"""Quiz generation service using Google Gemini API"""
import json
import logging
from typing import List, Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Only import genai if API key is configured
if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        HAS_GEMINI = True
    except Exception as e:
        logger.warning(f"Could not initialize Gemini API: {e}")
        HAS_GEMINI = False
else:
    logger.warning("GEMINI_API_KEY not configured - using dummy questions")
    HAS_GEMINI = False


class QuizGenerationService:
    """Service for generating quiz questions using Gemini LLM"""
    
    QUESTION_TYPES = ["MCQ", "true_false", "fill_blank"]
    DIFFICULTIES = ["easy", "medium", "hard"]
    
    # Prompts for question generation
    SYSTEM_PROMPT = """You are an expert educational content analyst and quiz question generator. 
Your task is to generate high-quality quiz questions from educational content. 
Always ensure questions are clear, educational, and appropriate for the given grade level and difficulty.
Generate diverse question types and ensure questions directly relate to the provided content.
Provide explanations for correct answers to help with learning.
"""
    
    @staticmethod
    def generate_questions_for_chunk(
        content_chunk: str,
        subject: str,
        topic: str,
        grade_level: int,
        chunk_id: str,
        num_questions: int = 3,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate quiz questions for a content chunk using Gemini API
        
        Args:
            content_chunk: The text content to generate questions from
            subject: Subject of the content
            topic: Topic within subject
            grade_level: Grade level of the content
            chunk_id: Source chunk identifier
            num_questions: Number of questions to generate
            difficulty: Specific difficulty level (if None, generates mixed)
            
        Returns:
            List of generated question dictionaries
        """
        
        if not HAS_GEMINI:
            logger.info("Gemini API not available. Using dummy questions.")
            return QuizGenerationService._generate_dummy_questions(
                num_questions, subject, topic, difficulty, content_chunk
            )
        
        try:
            model = genai.GenerativeModel(settings.MODEL_NAME)
            
            # Build difficulty specification
            difficulty_spec = f"with difficulty level: {difficulty}" if difficulty else "with mixed difficulty levels (easy, medium, hard)"
            
            prompt = f"""
Generate {num_questions} educational quiz questions for Grade {grade_level} students.

Subject: {subject}
Topic: {topic}
Content to base questions on:
{content_chunk[:500]}

Requirements:
1. Generate {num_questions} questions {difficulty_spec}
2. Include a mix of these question types (when possible):
   - Multiple Choice Questions (MCQ) with 4 options
   - True/False questions
   - Fill in the blank questions
3. Each question should test understanding of the provided content
4. Ensure questions are age-appropriate for grade {grade_level}
5. Provide clear correct answers
6. Include brief explanations for each answer

Return ONLY valid JSON array with no markdown formatting, no code block delimiters, and no additional text.
Each question must have this exact structure:
{{
    "question_text": "The question...",
    "question_type": "MCQ" or "true_false" or "fill_blank",
    "options": ["Option 1", "Option 2", ...],
    "correct_answer": "The correct answer",
    "difficulty": "easy" or "medium" or "hard",
    "explanation": "Why this is correct..."
}}

Return ONLY the JSON array without any markdown code blocks or explanations.
"""
            
            response = model.generate_content(prompt)
            
            if not response.text:
                logger.warning("Empty response from Gemini API, using dummy questions")
                return QuizGenerationService._generate_dummy_questions(
                    num_questions, subject, topic, difficulty, content_chunk
                )
            
            # Parse the response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            response_text = response_text.strip()
            
            questions = json.loads(response_text)
            
            # Validate and enhance questions
            validated_questions = []
            for question in questions:
                if all(key in question for key in ['question_text', 'question_type', 'correct_answer']):
                    question['subject'] = subject
                    question['topic'] = topic
                    question['source_chunk_id'] = chunk_id
                    question['grade_level'] = grade_level
                    validated_questions.append(question)
            
            if validated_questions:
                logger.info(f"Generated {len(validated_questions)} questions for chunk {chunk_id} using Gemini")
                return validated_questions
            else:
                logger.warning("No valid questions from Gemini, using dummy questions")
                return QuizGenerationService._generate_dummy_questions(
                    num_questions, subject, topic, difficulty, content_chunk
                )
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response from Gemini: {e}, using dummy questions")
            return QuizGenerationService._generate_dummy_questions(
                num_questions, subject, topic, difficulty, content_chunk
            )
        except Exception as e:
            logger.error(f"Error generating questions with Gemini: {e}, using dummy questions")
            return QuizGenerationService._generate_dummy_questions(
                num_questions, subject, topic, difficulty, content_chunk
            )
    
    @staticmethod
    def _generate_dummy_questions(
        num_questions: int,
        subject: str,
        topic: str,
        difficulty: Optional[str] = None,
        content: str = None
    ) -> List[Dict]:
        """Generate dummy questions for testing when API is not available"""
        
        content_preview = content[:100] if content else topic
        
        dummy_questions = [
            {
                "question_text": f"What is a key concept about {topic}?",
                "question_type": "MCQ",
                "options": [
                    f"{topic} is an important concept",
                    "It's not related to the subject",
                    "It's outdated information",
                    "It's a common misconception"
                ],
                "correct_answer": f"{topic} is an important concept",
                "difficulty": difficulty or "easy",
                "explanation": f"{topic} is a fundamental concept in {subject} education.",
                "subject": subject,
                "topic": topic,
            },
            {
                "question_text": f"{topic} is a core topic in {subject}.",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "True",
                "difficulty": difficulty or "medium",
                "explanation": f"{topic} is indeed a crucial aspect of {subject}.",
                "subject": subject,
                "topic": topic,
            },
            {
                "question_text": f"Understanding {topic} is essential for learning about ____.",
                "question_type": "fill_blank",
                "options": [],
                "correct_answer": subject,
                "difficulty": difficulty or "hard",
                "explanation": f"{topic} forms the foundation for understanding {subject}.",
                "subject": subject,
                "topic": topic,
            },
            {
                "question_text": f"Which statement best describes {topic}?",
                "question_type": "MCQ",
                "options": [
                    f"{topic} is a standard topic in {subject}",
                    "It's rarely taught anymore",
                    "It's only for advanced students",
                    "It was created recently"
                ],
                "correct_answer": f"{topic} is a standard topic in {subject}",
                "difficulty": difficulty or "medium",
                "explanation": f"{topic} has been an established part of {subject} curriculum.",
                "subject": subject,
                "topic": topic,
            },
            {
                "question_text": f"How does {topic} relate to {subject}?",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "True",
                "difficulty": difficulty or "hard",
                "explanation": f"{topic} is directly connected to various aspects of {subject}.",
                "subject": subject,
                "topic": topic,
            }
        ]
        
        selected = dummy_questions[:num_questions]
        logger.info(f"Generated {len(selected)} dummy questions for {topic}")
        return selected
    
    @staticmethod
    def generate_questions_batch(
        chunks: List[Dict],
        num_questions_per_chunk: int = 3
    ) -> List[Dict]:
        """
        Generate questions for multiple chunks
        
        Args:
            chunks: List of chunk dictionaries with content and metadata
            num_questions_per_chunk: Questions to generate per chunk
            
        Returns:
            List of all generated questions
        """
        all_questions = []
        
        for chunk in chunks:
            questions = QuizGenerationService.generate_questions_for_chunk(
                content_chunk=chunk['content'],
                subject=chunk['subject'],
                topic=chunk['topic'],
                grade_level=chunk['grade_level'],
                chunk_id=chunk['chunk_id'],
                num_questions=num_questions_per_chunk
            )
            all_questions.extend(questions)
        
        return all_questions
