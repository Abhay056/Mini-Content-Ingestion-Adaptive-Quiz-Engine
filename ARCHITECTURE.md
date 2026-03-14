"""Architecture and Design Document"""

# System Architecture

## Overview
The Mini Content Ingestion and Adaptive Quiz Engine is a comprehensive educational platform built with modern web technologies. It processes educational PDFs, generates AI-powered quiz questions, and delivers personalized learning experiences through adaptive difficulty adjustment.

## Core Components

### 1. API Layer (FastAPI)
- **Purpose**: RESTful endpoints for client interactions
- **Key Features**:
  - Async request handling for high concurrency
  - Automatic request validation with Pydantic
  - Built-in OpenAPI/Swagger documentation
  - CORS support for cross-origin requests

**Endpoints**:
- POST /api/ingest - Upload and process PDF
- GET /api/quiz - Retrieve quiz questions
- POST /api/submit-answer - Record student answers
- GET /api/student-progress/{student_id} - Get learner metrics

### 2. Service Layer
Orchestrates business logic and handles complex operations:

#### ContentIngestionService
- Coordinates PDF extraction, parsing, and storage
- Manages content chunking strategy
- Triggers quiz generation
- Maintains data consistency

#### PDFExtractionService
- Extracts raw text from PDF pages
- Cleans and normalizes extracted content
- Implements smart chunking with context overlap
- Extracts metadata from filenames

#### QuizGenerationService
- Interfaces with Google Gemini API
- Generates diverse question types (MCQ, T/F, Fill-in-blank)
- Ensures question-content traceability
- Handles API failures gracefully

#### AdaptiveDifficultyService
- Tracks student performance metrics
- Implements adaptive algorithms
- Manages difficulty level progression
- Calculates learning analytics

### 3. Data Access Layer (SQLAlchemy ORM)
Provides type-safe database interactions:

```
StudentProgress
  │
  ├── student_id (PK)
  ├── current_difficulty
  ├── accuracy_percentage (calculated)
  └── streaks (consecutive correct/incorrect)

Source (PDF Document)
  │
  ├── source_id (PK)
  ├── filename, subject, topic
  └── chunks ──→ ContentChunk
                  │
                  ├── chunk_id (PK)
                  ├── content_text
                  └── questions ──→ QuizQuestion
                                    │
                                    ├── question_id (PK)
                                    ├── question_text, type
                                    ├── options, correct_answer
                                    ├── difficulty
                                    └── answers ──→ StudentAnswer
                                                   │
                                                   ├── student_id
                                                   ├── selected_answer
                                                   └── is_correct
```

### 4. Database (PostgreSQL)
Enterprise-grade relational database:
- ACID compliance for data integrity
- Efficient indexing on frequently queried columns
- Relationship constraints ensure referential integrity
- Connection pooling for performance

## Data Processing Pipeline

### Content Ingestion Pipeline
```
1. PDF Upload
   ↓
2. Size & Type Validation
   ↓
3. File Storage
   ↓
4. Text Extraction (pypdf)
   ↓
5. Text Cleaning
   - Remove OCR artifacts
   - Normalize whitespace
   - Handle special characters
   ↓
6. Content Chunking
   - 500 char target size
   - 100 char overlap
   - Sentence boundary respect
   ↓
7. Metadata Extraction
   - Grade level from filename
   - Subject identification
   - Topic extraction
   ↓
8. Source & Chunk Storage
   ↓
9. Quiz Generation (Gemini)
   - 3 questions per chunk
   - Mixed difficulty levels
   - Diverse question types
   ↓
10. Question Storage with Traceability
```

### Quiz Delivery Pipeline
```
1. Quiz Request
   ├── topic/subject filters?
   ├── student_id provided?
   └── explicit difficulty?
   ↓
2. Adaptive Difficulty Resolution
   └── If student_id: fetch current_difficulty
   └── Else: use INITIAL_DIFFICULTY
   ↓
3. Question Query
   └── Filter by subject/topic/difficulty
   ├── Limit results
   └── Return JSON with options parsed
   ↓
4. Response Formatting
   └── Convert each question to QuizQuestionSchema
   ├── Parse options JSON
   └── Include explanations
```

### Student Answer Pipeline
```
1. Answer Submission
   ├── student_id
   ├── question_id
   ├── selected_answer
   └── time_spent_seconds
   ↓
2. Question Validation
   └── Verify question exists
   └── Retrieve correct answer
   ↓
3. Answer Evaluation
   └── Case-insensitive comparison
   └── Determine is_correct boolean
   ↓
4. Store StudentAnswer Record
   ↓
5. Update Student Progress
   ├── Increment total_questions_answered
   ├── Update correct/incorrect counts
   ├── Track consecutive streaks
   └── Evaluate difficulty adjustment
   ↓
6. Apply Adaptive Logic
   ├── 2+ consecutive correct → increase difficulty
   ├── 2+ consecutive incorrect → decrease difficulty
   └── Respect boundaries (easy-hard)
   ↓
7. Return Feedback
   ├── is_correct status
   ├── explanation
   ├── new_difficulty
   └── accuracy_percentage
```

## Adaptive Difficulty Algorithm (Detailed)

### Difficulty Progression
```
Level 0: EASY
  ↓ (2 consecutive correct)
Level 1: MEDIUM
  ↓ (2 consecutive correct)
Level 2: HARD
  ↑ (2 consecutive incorrect)
```

### State Machine
```
State: current_difficulty, consecutive_correct, consecutive_incorrect

Transition on Correct Answer:
  consecutive_correct += 1
  consecutive_incorrect = 0
  
  IF consecutive_correct >= 2:
    new_level = min(current_level + 1, MAX)
    current_difficulty = LEVELS[new_level]
    consecutive_correct = 0

Transition on Incorrect Answer:
  consecutive_incorrect += 1
  consecutive_correct = 0
  
  IF consecutive_incorrect >= 2:
    new_level = max(current_level - 1, 0)
    current_difficulty = LEVELS[new_level]
    consecutive_incorrect = 0
```

### Performance Metrics
- **Accuracy**: (correct / total) × 100
- **Streak**: Consecutive correct/incorrect answers
- **Difficulty**: Current challenge level (easy/medium/hard)
- **Activity**: Last quiz completion timestamp

## Error Handling Strategy

### API Layer
- Pydantic validates all inputs
- HTTP status codes:
  - 400: Invalid request
  - 404: Resource not found
  - 413: File too large
  - 500: Server error

### Service Layer
- Graceful LLM API fallback with dummy questions
- Database transaction rollback on errors
- Comprehensive logging at each stage

### Database Layer
- Connection pooling with health checks
- Retry logic for transient failures
- Foreign key constraints prevent orphaned records

## Security Considerations

### Current Implementation
- Environment variables for secrets (not hardcoded)
- Input validation on all API endpoints
- PDF file size limits
- Database connection encryption (via connection string)

### Recommended Enhancements
- JWT authentication for API endpoints
- Rate limiting to prevent abuse
- Input sanitization for stored content
- HTTPS enforcement in production
- API key management for Gemini

## Performance Optimization

### Database
- Indexes on frequently filtered columns:
  - student_id, difficulty, topic, subject
- Connection pooling reduces overhead
- Query optimization: use joins instead of N+1
- Lazy loading for relationships

### API
- Async/await for non-blocking I/O
- Caching question responses (future)
- Background task queue for PDF processing (future)
- Pagination for large result sets (future)

### LLM
- Batching questions per chunk
- Caching for identical content
- Fallback to dummy questions on API failure
- Rate limit management

## Scalability

### Current Limits
- Single server deployment
- Single database instance
- Synchronous file processing
- Real-time API responses

### Future Scaling
- Load balancer for multi-instance deployment
- Database replication for read scaling
- Celery/RQ for async task processing
- Redis for caching and session management
- CDN for static content
- Microservices for specialized functions

## Testing Strategy

### Unit Tests
- Data model validation
- Service layer logic
- Utility functions (text cleaning, parsing)

### Integration Tests
- End-to-end API flows
- Database transactions
- Error scenarios

### Performance Tests
- PDF processing speed
- Question generation latency
- Query response times
- Concurrent user handling

## Deployment Architecture

### Development
```
Local Machine
├── Python Virtual Env
├── PostgreSQL (local)
├── FastAPI dev server
└── Gemini API (cloud)
```

### Production (Recommended)
```
Cloud Provider (AWS/GCP/Azure)
├── Load Balancer
├── FastAPI instances (Docker)
├── PostgreSQL RDS
├── Redis Cache
└── Object Storage (PDFs)
```

## Technology Justification

### Why FastAPI?
- Modern Python async/await support
- Automatic API documentation
- Built-in request validation
- High performance (similar to Go/Node)
- Growing ecosystem and community

### Why PostgreSQL?
- Mature, stable relational DB
- ACID compliance
- Strong consistency
- JSON features for metadata
- Horizontal scaling options

### Why Gemini?
- State-of-the-art language model
- Quality question generation
- Reasonable API pricing
- Easy integration
- No training required

### Why SQLAlchemy?
- Database-agnostic ORM
- Type hints support
- Efficient query generation
- Relationship management
- Data migration tools (Alembic)

---

Last Updated: March 2024
Version: 1.0.0
