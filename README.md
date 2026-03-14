# Mini Content Ingestion and Adaptive Quiz Engine

A comprehensive system for ingesting educational PDF content, generating quiz questions using AI, and providing adaptive learning experiences through intelligent difficulty adjustment.

## Overview

This system implements a complete educational content management and assessment platform with the following key features:

1. **PDF Content Ingestion**: Extracts, cleans, and chunks educational content from PDF files
2. **AI Quiz Generation**: Uses Google Gemini to generate diverse question types from extracted content
3. **Structured Storage**: Maintains content, questions, and student progress in a PostgreSQL database
4. **Dynamic Quiz Delivery**: Serves questions through REST API with filtering and adaptive selection
5. **Adaptive Difficulty**: Automatically adjusts quiz difficulty based on student performance
6. **Student Progress Tracking**: Comprehensive analytics on student performance and learning patterns

## System Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT APPLICATIONS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│                    FastAPI REST API Server                       │
│  ┌──────────────┬──────────────┬──────────────┐                  │
│  │   Ingestion  │   Quiz       │  Student     │                  │
│  │   Routes     │   Routes     │  Routes      │                  │
│  └──────────────┴──────────────┴──────────────┘                  │
│           ↓              ↓              ↓                         │
├─────────────────────────────────────────────────────────────────┤
│                      SERVICE LAYER                               │
│  ┌──────────────────┬──────────────────────┐                     │
│  │ PDF Extraction   │  Quiz Generation     │                     │
│  │ Content Chunking │  (Gemini LLM)        │                     │
│  └──────────────────┴──────────────────────┘                     │
│  ┌──────────────────────────────────────────┐                    │
│  │  Adaptive Difficulty & Student Progress  │                    │
│  └──────────────────────────────────────────┘                    │
│           ↓              ↓              ↓                         │
├─────────────────────────────────────────────────────────────────┤
│                    DATA ACCESS LAYER                             │
│              SQLAlchemy ORM Models                               │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                   POSTGRESQL DATABASE                            │
│  ┌────────┬──────────────┬──────────────┬─────────────┐          │
│  │source  │content_chunks│quiz_questions│student_     │          │
│  │        │              │              │progress     │          │
│  └────────┴──────────────┴──────────────┴─────────────┘          │
│  ┌──────────────┐                                                │
│  │student_answers                                               │
│  └──────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Data Models

### 1. Content Management Models

#### Source (PDF Documents)
```
{
  "source_id": "SRC_ABC123D4",  // Unique identifier
  "filename": "peblo_pdf_grade4_english_grammar.pdf",
  "subject": "English",
  "topic": "Grammar",
  "grade_level": 4,
  "file_path": "./pdfs/peblo_pdf_grade4_english_grammar.pdf",
  "uploaded_at": "2024-03-14T10:00:00",
  "content_summary": "First 500 characters of content...",
  "chunks": [ContentChunk, ...]
}
```

#### ContentChunk (Segmented Content)
```
{
  "chunk_id": "SRC_ABC123D4_CH_00",
  "source_id": 1,  // FK to Source
  "grade_level": 4,
  "subject": "English",
  "topic": "Grammar",
  "content_text": "A noun is a word that represents...",
  "chunk_index": 0,
  "created_at": "2024-03-14T10:00:00"
}
```

### 2. Quiz Models

#### QuizQuestion (Generated Questions)
```
{
  "question_id": "SRC_ABC123D4_Q000",
  "source_chunk_id": 1,  // FK to ContentChunk
  "question_text": "What is a noun?",
  "question_type": "MCQ",  // MCQ, true_false, fill_blank
  "options": ["A word that represents a person/thing", "An action", "A feeling"],
  "correct_answer": "A word that represents a person/thing",
  "difficulty": "easy",  // easy, medium, hard
  "subject": "English",
  "topic": "Grammar",
  "explanation": "A noun is one of the main parts of speech...",
  "generated_at": "2024-03-14T10:05:00"
}
```

#### StudentAnswer (Student Responses)
```
{
  "student_id": "S001",
  "question_id": 1,  // FK to QuizQuestion
  "selected_answer": "A word that represents a person/thing",
  "is_correct": true,
  "time_spent_seconds": 45,
  "submitted_at": "2024-03-14T10:10:00"
}
```

#### StudentProgress (Adaptive Difficulty Tracking)
```
{
  "student_id": "S001",
  "current_difficulty": "medium",
  "total_questions_answered": 25,
  "correct_answers": 20,
  "incorrect_answers": 5,
  "consecutive_correct": 2,
  "consecutive_incorrect": 0,
  "accuracy_percentage": 80.0,
  "last_activity": "2024-03-14T10:10:00"
}
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1 - Modern, fast Python web framework
- **Web Server**: Uvicorn - ASGI server for async Python applications
- **ORM**: SQLAlchemy 2.0 - SQL toolkit and ORM

### Database
- **Primary DB**: PostgreSQL - Robust relational database
- **Driver**: psycopg2-binary - PostgreSQL adapter for Python

### AI/ML
- **LLM**: Google Generative AI (Gemini) - State-of-the-art language model
- **Model**: gemini-pro - Latest Gemini model for text generation

### PDF Processing
- **PDF Library**: pypdf 3.17.1 - PDF reading and text extraction

### Development Tools
- **Testing**: pytest, pytest-asyncio - Testing framework
- **HTTP Client**: httpx - Async HTTP client for testing
- **Validation**: Pydantic 2.5 - Data validation using Python type hints

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 12 or higher
- Git

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd "Mini Content Ingestion and Adaptive Quiz Engine"
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
```bash
# Copy example file
cp .env.example .env

# Edit .env with your configuration
# Key settings to update:
# - DATABASE_URL: PostgreSQL connection string
# - GEMINI_API_KEY: Your Google Gemini API key
```

#### Getting API Keys

**Google Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key to your `.env` file

**PostgreSQL Setup:**
```bash
# If using PostgreSQL locally
createdb quiz_engine

# Update DATABASE_URL in .env:
# DATABASE_URL=postgresql://your_user:your_password@localhost:5432/quiz_engine
```

### Step 5: Initialize Database
The database will be automatically initialized on first application startup. Tables will be created based on SQLAlchemy models.

### Step 6: Run Application
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

## API Endpoints

### Health & Status
- `GET /` - Root endpoint with service information
- `GET /health` - Health check endpoint

### Content Ingestion

#### Upload and Ingest PDF
```
POST /api/ingest
Content-Type: multipart/form-data

Form Parameters:
  - file: <PDF file>
  - generate_quizzes: true (default)
  - questions_per_chunk: 3 (default)

Response:
{
  "source_id": "SRC_ABC123D4",
  "filename": "peblo_pdf_grade4_english_grammar.pdf",
  "chunks_created": 10,
  "subject": "English",
  "topic": "Grammar",
  "grade_level": 4,
  "questions_generated": 30,
  "message": "Successfully ingested..."
}
```

#### Get Ingestion Status
```
GET /api/ingest/status/{source_id}

Response:
{
  "source_id": "SRC_ABC123D4",
  "total_chunks": 10,
  "questions_generated": 30,
  "generation_time_seconds": 45.5,
  "status": "completed",
  "message": "Ingestion and quiz generation completed successfully"
}
```

### Quiz Delivery

#### Get Quiz Questions (with Adaptive Difficulty)
```
GET /api/quiz?topic=Grammar&difficulty=medium&limit=5&student_id=S001

Query Parameters:
  - topic: Filter by topic (optional)
  - subject: Filter by subject (optional)
  - difficulty: easy|medium|hard (optional, uses adaptive if student_id provided)
  - limit: 1-50 questions (default: 5)
  - student_id: For adaptive difficulty (optional)

Response:
[
  {
    "question_id": "SRC_ABC123D4_Q001",
    "question_text": "What is a noun?",
    "question_type": "MCQ",
    "options": ["A word that represents...", "An action", "A feeling"],
    "difficulty": "easy",
    "subject": "English",
    "topic": "Grammar",
    "explanation": "A noun is one of the main parts of speech..."
  },
  ...
]
```

#### Get Quiz by Subject
```
GET /api/quiz/by-subject/English?limit=5&difficulty=medium

Response:
[...list of questions...]
```

#### Get Quiz by Topic
```
GET /api/quiz/by-topic/Grammar?limit=5

Response:
[...list of questions...]
```

### Student Interactions

#### Submit Student Answer
```
POST /api/submit-answer

Request Body:
{
  "student_id": "S001",
  "question_id": "SRC_ABC123D4_Q001",
  "selected_answer": "A word that represents a person/thing",
  "time_spent_seconds": 45
}

Response:
{
  "is_correct": true,
  "correct_answer": "A word that represents a person/thing",
  "explanation": "A noun is one of the main parts of speech...",
  "current_difficulty": "medium",
  "accuracy_percentage": 85.5
}
```

#### Get Student Progress
```
GET /api/student-progress/{student_id}

Response:
{
  "student_id": "S001",
  "current_difficulty": "medium",
  "total_questions_answered": 25,
  "correct_answers": 20,
  "incorrect_answers": 5,
  "accuracy_percentage": 80.0,
  "consecutive_correct": 2,
  "consecutive_incorrect": 0,
  "last_activity": "2024-03-14T10:10:00"
}
```

## Adaptive Difficulty Algorithm

The system implements an intelligent adaptive difficulty system that adjusts quiz difficulty based on student performance:

### Algorithm Logic

1. **Initial State**: Students start at "medium" difficulty

2. **Answer Evaluation**:
   - Correct answer: increment consecutive_correct counter
   - Incorrect answer: increment consecutive_incorrect counter

3. **Difficulty Adjustment**:
   - **Difficulty Increase**: 
     - Trigger: 2 consecutive correct answers
     - New difficulty: Move up one level (easy → medium → hard)
     - Reset consecutive_correct counter
   - **Difficulty Decrease**:
     - Trigger: 2 consecutive incorrect answers
     - New difficulty: Move down one level (hard → medium → easy)
     - Reset consecutive_incorrect counter

4. **Boundaries**:
   - Easy: Minimum difficulty level
   - Hard: Maximum difficulty level
   - Will not go below "easy" or above "hard"

5. **Question Selection**:
   - When retrieving new questions, the system uses the student's current difficulty level
   - Questions are filtered to match the student's adaptive difficulty
   - Optional: Instructors can override with explicit difficulty parameter

### Performance Tracking

- **Accuracy Percentage**: `(correct_answers / total_questions_answered) * 100`
- **Consecutive Tracking**: Supports streaks for more responsive adaptation
- **Recommended Difficulty** (future enhancement):
  - 80%+ accuracy: Recommend "hard"
  - 60-80% accuracy: Recommend "medium"
  - <60% accuracy: Recommend "easy"

## Content Processing Pipeline

### PDF Ingestion Flow

1. **File Upload**
   - Validate file type (PDF only)
   - Validate file size (max 50MB)
   - Store in `/pdfs` directory

2. **Text Extraction**
   - Extract text from all PDF pages
   - Preserve page structure where possible
   - Remove extra whitespace and artifacts

3. **Text Cleaning**
   - Remove OCR errors and special characters
   - Normalize whitespace
   - Fix common text artifacts

4. **Content Chunking**
   - Split content into ~500 character chunks
   - Maintain context with 100-character overlap
   - Ensure minimum chunk size (50 characters)
   - Respect sentence boundaries

5. **Metadata Extraction**
   - Extract grade level from filename pattern (grade1-12)
   - Identify subject from filename keywords
   - Extract topic from remaining filename components

6. **Database Storage**
   - Create Source record for PDF
   - Store each chunk as ContentChunk
   - Link chunks to source document

7. **Quiz Generation**
   - Process each chunk through Gemini API
   - Generate 3 question types: MCQ, True/False, Fill-in-the-Blank
   - Generate mixed difficulty levels
   - Store questions with source traceability

## Example Usage Workflow

### 1. Ingest Educational Material
```bash
# Upload a PDF
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@peblo_pdf_grade4_english_grammar.pdf" \
  -F "generate_quizzes=true" \
  -F "questions_per_chunk=3"

# Response
{
  "source_id": "SRC_A1B2C3D4",
  "chunks_created": 8,
  "questions_generated": 24
}
```

### 2. Student Takes Quiz
```bash
# Get personalized quiz for student
curl "http://localhost:8000/api/quiz?limit=5&student_id=alice"

# Response: 5 questions at Alice's current difficulty level
```

### 3. Student Submits Answer
```bash
curl -X POST http://localhost:8000/api/submit-answer \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "alice",
    "question_id": "SRC_A1B2C3D4_Q001",
    "selected_answer": "A noun is a word that represents a person, place, or thing",
    "time_spent_seconds": 30
  }'

# Response
{
  "is_correct": true,
  "explanation": "Correct! A noun is indeed...",
  "current_difficulty": "medium",
  "accuracy_percentage": 85.0
}
```

### 4. Monitor Progress
```bash
# Get student progress
curl "http://localhost:8000/api/student-progress/alice"

# Response
{
  "student_id": "alice",
  "current_difficulty": "hard",
  "total_questions_answered": 50,
  "accuracy_percentage": 88.0,
  "consecutive_correct": 3
}
```

## Testing

### Run Unit Tests
```bash
pytest tests/ -v

# Run specific test file
pytest tests/test_pdf_extraction.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Manual API Testing

Use the built-in Swagger UI:
1. Navigate to `http://localhost:8000/docs`
2. Expand endpoint sections
3. Click "Try it out"
4. Enter parameters and execute

Or use curl/Postman for more complex requests.

## Configuration Guide

### Environment Variables

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/quiz_engine

# Gemini API Key
GEMINI_API_KEY=your_api_key_here

# Application Settings
APP_ENV=development
DEBUG=True
LOG_LEVEL=INFO

# PDF Processing
MAX_PDF_SIZE_MB=50
PDF_UPLOAD_DIR=./pdfs

# Quiz Generation
MODEL_NAME=gemini-pro
TEMPERATURE=0.7
MAX_TOKENS=2048

# Adaptive Difficulty
DIFFICULTY_LEVELS=easy,medium,hard
INITIAL_DIFFICULTY=medium
MAX_DIFFICULTY_INCREASE_PER_CORRECT=1
MAX_DIFFICULTY_DECREASE_PER_INCORRECT=1
```

### Performance Tuning

**Database Connection Pool**:
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Increase for high concurrency
    max_overflow=20,  # Allow additional connections when needed
)
```

**Chunk Size for Content**:
```python
# In PDFExtractionService
CHUNK_SIZE = 500  # Adjust based on content characteristics
OVERLAP = 100    # Context preservation between chunks
```

**LLM Generation Parameters**:
```env
TEMPERATURE=0.7     # 0=deterministic, 1=creative
MAX_TOKENS=2048     # Maximum response length
```

## Project Structure

```
Mini Content Ingestion and Adaptive Quiz Engine/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database setup and sessions
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── content.py          # Source and ContentChunk models
│   │   └── quiz.py             # Quiz and student models
│   │
│   ├── schemas/
│   │   └── __init__.py         # Pydantic request/response schemas
│   │
│   ├── services/
│   │   ├── __init__.py         # PDF extraction service
│   │   ├── quiz_generation.py  # Gemini-based quiz generation
│   │   ├── adaptive_difficulty.py  # Adaptive logic service
│   │   └── ingestion.py        # Content ingestion orchestration
│   │
│   └── api/
│       ├── __init__.py
│       ├── ingestion.py        # PDF ingestion endpoints
│       └── quiz.py             # Quiz operation endpoints
│
├── tests/
│   └── test_*.py              # Unit and integration tests
│
├── pdfs/                       # Uploaded PDF files storage
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Local environment (not committed)
├── .gitignore                # Git ignore patterns
└── README.md                 # This file
```

## Troubleshooting

### Database Connection Issues
```
Error: could not translate host name "localhost" to address
Solution: Ensure PostgreSQL is running and DATABASE_URL is correct
```

### PDF Extraction Issues
```
Error: PdfReader requires a PDF file
Solution: Ensure uploaded file is a valid PDF and not corrupted
```

### Gemini API Issues
```
Error: APIError with status 403
Solution: Verify GEMINI_API_KEY is correct and has proper permissions
```

### Memory Issues
```
Error: MemoryError when processing large PDFs
Solution: Increase CHUNK_SIZE or process PDFs in smaller batches
```

## Future Enhancements

1. **Question Quality Assessment**
   - Implement question discrimination index
   - Track question difficulty calibration
   - Auto-retire poorly performing questions

2. **Advanced Analytics**
   - Learning curve analysis
   - Concept mastery tracking
   - Personalized learning paths

3. **Multi-language Support**
   - Support for multiple languages in PDF ingestion
   - Adaptive difficulty based on language proficiency

4. **Caching & Performance**
   - Implement Redis caching for frequently accessed questions
   - Question recommendation pre-computation
   - Database query optimization

5. **Collaborative Features**
   - Teacher dashboard for class progress
   - Peer learning analytics
   - Adaptive group formation

6. **Advanced LLM Features**
   - Multi-turn question clarification
   - Hint generation based on performance
   - Explanation quality scoring

## License

This project is provided as-is for educational and research purposes.

## Support

For issues, questions, or contributions, please:
1. Check existing documentation
2. Review API error responses  
3. Check logs in application output
4. Open an issue with detailed error information

## Contributors

- AI Content Generation and Architecture Design

---

**Last Updated**: March 2024
**Version**: 1.0.0
