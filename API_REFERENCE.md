"""Complete API Reference and Examples"""

# Mini Content Ingestion & Adaptive Quiz Engine - API Reference

## Base URL
```
http://localhost:8000
```

## Server Information
- **Host**: 0.0.0.0
- **Port**: 8000
- **Documentation**: http://localhost:8000/docs (Swagger UI)

---

## Health & Diagnostic Endpoints

### 1. Health Check
Verify server is running

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "app": "Quiz Engine",
  "version": "1.0.0"
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

### 2. Root Information
Get application metadata

**Endpoint**: `GET /`

**Response**:
```json
{
  "message": "Mini Content Ingestion and Adaptive Quiz Engine",
  "version": "1.0.0",
  "status": "operational",
  "docs_url": "/docs",
  "openapi_url": "/openapi.json"
}
```

**Example**:
```bash
curl http://localhost:8000/
```

---

## Content Ingestion Endpoints

### 1. Upload and Ingest PDF
Extract content and generate quiz questions from PDF

**Endpoint**: `POST /api/ingest`

**Parameters** (form-data):
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| file | file (PDF) | Yes | - | PDF file to ingest |
| generate_quizzes | boolean | No | true | Automatically generate quiz questions |
| questions_per_chunk | integer | No | 3 | Number of questions per chunk |

**Request**:
```bash
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@peblo_pdf_grade4_english_grammar.pdf" \
  -F "generate_quizzes=true" \
  -F "questions_per_chunk=3"
```

**Success Response** (200):
```json
{
  "source_id": "SRC_A1B2C3D4",
  "filename": "peblo_pdf_grade4_english_grammar.pdf",
  "chunks_created": 8,
  "subject": "English",
  "topic": "Grammar",
  "grade_level": 4,
  "questions_generated": 24,
  "message": "Successfully ingested peblo_pdf_grade4_english_grammar.pdf with 8 chunks"
}
```

**Error Responses**:
- 400: File type not PDF
- 413: File size exceeds limit
- 500: Processing error

---

### 2. Get Ingestion Status
Check quiz generation status for a source

**Endpoint**: `GET /api/ingest/status/{source_id}`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| source_id | string | Yes | Source document ID (e.g., SRC_A1B2C3D4) |

**Request**:
```bash
curl http://localhost:8000/api/ingest/status/SRC_A1B2C3D4
```

**Success Response** (200):
```json
{
  "source_id": "SRC_A1B2C3D4",
  "total_chunks": 8,
  "questions_generated": 24,
  "generation_time_seconds": 45.2,
  "status": "completed",
  "message": "Ingestion and quiz generation completed successfully"
}
```

**Error Responses**:
- 404: Source not found
- 500: Server error

---

## Quiz Delivery Endpoints

### 1. Get Quiz Questions (Universal Endpoint)
Retrieve quiz questions with flexible filtering

**Endpoint**: `GET /api/quiz`

**Query Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| topic | string | No | null | Filter by topic (e.g., "Grammar") |
| subject | string | No | null | Filter by subject (e.g., "English") |
| difficulty | string | No | null | Filter by difficulty: easy, medium, hard |
| limit | integer | No | 5 | Number of questions (1-50) |
| student_id | string | No | null | Enable adaptive difficulty |

**Request Examples**:

Basic request (5 medium questions):
```bash
curl "http://localhost:8000/api/quiz"
```

With filters:
```bash
curl "http://localhost:8000/api/quiz?topic=Grammar&subject=English&limit=10"
```

With adaptive difficulty:
```bash
curl "http://localhost:8000/api/quiz?student_id=alice123&limit=5"
```

Mixed parameters:
```bash
curl "http://localhost:8000/api/quiz?topic=Shapes&difficulty=easy&limit=3&student_id=bob456"
```

**Success Response** (200):
```json
[
  {
    "question_id": "SRC_A1B2C3D4_Q001",
    "question_text": "What is a noun?",
    "question_type": "MCQ",
    "options": [
      "A word that represents a person, place, or thing",
      "An action verb",
      "A descriptive word",
      "A connecting word"
    ],
    "difficulty": "easy",
    "subject": "English",
    "topic": "Grammar",
    "explanation": "A noun is one of the main parts of speech that names a person, place, thing, or idea."
  },
  {
    "question_id": "SRC_A1B2C3D4_Q002",
    "question_text": "Pronouns replace nouns in sentences.",
    "question_type": "true_false",
    "options": ["True", "False"],
    "difficulty": "easy",
    "subject": "English",
    "topic": "Grammar",
    "explanation": "True. Pronouns are words that take the place of nouns in sentences."
  },
  {
    "question_id": "SRC_A1B2C3D4_Q003",
    "question_text": "A word that describes a noun is called a(n) ____.",
    "question_type": "fill_blank",
    "options": [],
    "difficulty": "medium",
    "subject": "English",
    "topic": "Grammar",
    "explanation": "The answer is 'adjective'. Adjectives modify or describe nouns."
  }
]
```

**Error Responses**:
- 404: No questions matching criteria
- 500: Server error

---

### 2. Get Quiz by Subject
Convenience endpoint for subject-based filtering

**Endpoint**: `GET /api/quiz/by-subject/{subject}`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| subject | string | Yes | Subject name (e.g., "English", "Math") |

**Query Parameters**:
| Name | Type | Default | Description |
|------|------|---------|-------------|
| difficulty | string | null | easy, medium, or hard |
| limit | integer | 5 | Number of questions (1-50) |

**Request**:
```bash
curl "http://localhost:8000/api/quiz/by-subject/English?difficulty=medium&limit=5"
```

**Success Response** (200):
Same as `/api/quiz` endpoint

---

### 3. Get Quiz by Topic
Convenience endpoint for topic-based filtering

**Endpoint**: `GET /api/quiz/by-topic/{topic}`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| topic | string | Yes | Topic name (e.g., "Grammar", "Shapes") |

**Query Parameters**:
| Name | Type | Default | Description |
|------|------|---------|-------------|
| difficulty | string | null | easy, medium, or hard |
| limit | integer | 5 | Number of questions (1-50) |

**Request**:
```bash
curl "http://localhost:8000/api/quiz/by-topic/Grammar?difficulty=easy&limit=3"
```

**Success Response** (200):
Same as `/api/quiz` endpoint

---

## Student Interaction Endpoints

### 1. Submit Answer
Submit a student's answer and receive feedback

**Endpoint**: `POST /api/submit-answer`

**Request Body** (application/json):
```json
{
  "student_id": "alice123",
  "question_id": "SRC_A1B2C3D4_Q001",
  "selected_answer": "A word that represents a person, place, or thing",
  "time_spent_seconds": 45
}
```

**Field Descriptions**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| student_id | string | Yes | Unique student identifier |
| question_id | string | Yes | ID of the question being answered |
| selected_answer | string | Yes | The answer selected by student |
| time_spent_seconds | integer | No | Seconds spent on this question |

**Request**:
```bash
curl -X POST http://localhost:8000/api/submit-answer \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "alice123",
    "question_id": "SRC_A1B2C3D4_Q001",
    "selected_answer": "A word that represents a person, place, or thing",
    "time_spent_seconds": 45
  }'
```

**Success Response** (200):
```json
{
  "is_correct": true,
  "correct_answer": "A word that represents a person, place, or thing",
  "explanation": "A noun is one of the main parts of speech that names a person, place, thing, or idea.",
  "current_difficulty": "medium",
  "accuracy_percentage": 85.5
}
```

**Error Responses**:
- 404: Question not found
- 500: Server error

**Key Response Fields**:
- `is_correct`: Whether the answer matches the correct answer
- `correct_answer`: The actual correct answer
- `explanation`: Why the answer is correct
- `current_difficulty`: Student's new adaptive difficulty level
- `accuracy_percentage`: Student's overall accuracy percentage

---

### 2. Get Student Progress
Retrieve student performance metrics and adaptive difficulty

**Endpoint**: `GET /api/student-progress/{student_id}`

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| student_id | string | Yes | Student identifier |

**Request**:
```bash
curl http://localhost:8000/api/student-progress/alice123
```

**Success Response** (200):
```json
{
  "student_id": "alice123",
  "current_difficulty": "hard",
  "total_questions_answered": 50,
  "correct_answers": 42,
  "incorrect_answers": 8,
  "accuracy_percentage": 84.0,
  "consecutive_correct": 3,
  "consecutive_incorrect": 0,
  "last_activity": "2024-03-14T15:30:00"
}
```

**Response Field Descriptions**:
| Field | Type | Description |
|-------|------|-------------|
| student_id | string | Student identifier |
| current_difficulty | string | Current adaptive difficulty (easy/medium/hard) |
| total_questions_answered | integer | Total questions attempted |
| correct_answers | integer | Number of correct responses |
| incorrect_answers | integer | Number of incorrect responses |
| accuracy_percentage | float | Calculated accuracy (0-100) |
| consecutive_correct | integer | Current streak of correct answers |
| consecutive_incorrect | integer | Current streak of incorrect answers |
| last_activity | datetime | Timestamp of last quiz activity |

**Error Responses**:
- 500: Server error

**Note**: If student doesn't exist, a new record is created with default values.

---

## Data Formats

### Question Types
- **MCQ**: Multiple Choice Question with 4 options
- **true_false**: Boolean question (True/False)
- **fill_blank**: Fill in the blank with a word/phrase

### Difficulty Levels
- **easy**: Fundamental concepts, basic understanding
- **medium**: Standard complexity, application of concepts
- **hard**: Advanced concepts, analysis and synthesis

### Adaptive Difficulty Logic
- Start: **medium**
- After 2 consecutive correct: increase difficulty level
- After 2 consecutive incorrect: decrease difficulty level
- Boundaries: cannot go below easy or above hard

---

## Status Codes

### Success Responses
- **200 OK**: Successful request
- **201 Created**: Resource created successfully

### Client Errors
- **400 Bad Request**: Invalid request format or parameters
- **404 Not Found**: Requested resource doesn't exist
- **413 Payload Too Large**: File size exceeds limit

### Server Errors
- **500 Internal Server Error**: Server processing error

---

## Error Response Format

All error responses follow this format:
```json
{
  "detail": "Error description message"
}
```

**Example Error**:
```json
{
  "detail": "Question SRC_ABC123_Q999 not found"
}
```

---

## Common Use Cases

### Scenario 1: Teacher Uploads Educational Material
```bash
# Upload PDF
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@lesson_plan.pdf" \
  -F "generate_quizzes=true"

# Response includes source_id for tracking
# Questions are automatically generated
```

### Scenario 2: Student Takes Adaptive Quiz
```bash
# Get personalized quiz for student
curl "http://localhost:8000/api/quiz?student_id=alice&limit=5"

# Student answers first question
curl -X POST http://localhost:8000/api/submit-answer \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "alice",
    "question_id": "SRC_XYZ_Q001",
    "selected_answer": "Answer"
  }'

# Next quiz request automatically uses updated difficulty
curl "http://localhost:8000/api/quiz?student_id=alice&limit=5"
```

### Scenario 3: Monitor Student Progress
```bash
# Check student's performance dashboard
curl http://localhost:8000/api/student-progress/alice

# Response shows:
# - Current difficulty level
# - Accuracy percentage
# - Learning streaks
# - Last activity
```

### Scenario 4: Review Specific Topics
```bash
# Get all medium-difficulty grammar questions
curl "http://localhost:8000/api/quiz/by-topic/Grammar?difficulty=medium&limit=10"

# Or all math questions
curl "http://localhost:8000/api/quiz/by-subject/Math?limit=10"
```

---

## Rate Limiting (Future)
Current implementation has no rate limiting. For production deployment, consider implementing:
- Per-student request limits
- Concurrent request limits
- API token-based throttling

---

## Pagination (Future)
Current implementation returns exact limit. For large datasets, consider:
- Cursor-based pagination
- Offset/limit pagination with sorting

---

## OpenAPI Specification
Access the machine-readable API specification:
```
GET /openapi.json
```

Browser-based interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**Document Version**: 1.0.0  
**Last Updated**: March 2024
