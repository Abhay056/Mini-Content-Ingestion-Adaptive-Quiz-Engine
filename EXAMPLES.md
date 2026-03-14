"""Example usage scenarios and integration tests"""

import json

# Example 1: PDF Ingestion Request
INGEST_REQUEST_EXAMPLE = {
    "description": "Upload a PDF file for content extraction and quiz generation",
    "endpoint": "POST /api/ingest",
    "request": """
curl -X POST http://localhost:8000/api/ingest \\
  -F "file=@peblo_pdf_grade4_english_grammar.pdf" \\
  -F "generate_quizzes=true" \\
  -F "questions_per_chunk=3"
    """,
    "response": {
        "source_id": "SRC_A1B2C3D4",
        "filename": "peblo_pdf_grade4_english_grammar.pdf",
        "chunks_created": 8,
        "subject": "English",
        "topic": "Grammar",
        "grade_level": 4,
        "questions_generated": 24,
        "message": "Successfully ingested peblo_pdf_grade4_english_grammar.pdf with 8 chunks"
    }
}

# Example 2: Get Quiz Questions
GET_QUIZ_EXAMPLE = {
    "description": "Retrieve 5 medium-difficulty grammar questions",
    "endpoint": "GET /api/quiz",
    "request": """
curl "http://localhost:8000/api/quiz?topic=Grammar&difficulty=medium&limit=5"
    """,
    "response": [
        {
            "question_id": "SRC_A1B2C3D4_Q001",
            "question_text": "What is a noun?",
            "question_type": "MCQ",
            "options": [
                "A word that represents a person, place, or thing",
                "An action performed",
                "A descriptive quality",
                "A connecting word"
            ],
            "difficulty": "easy",
            "subject": "English",
            "topic": "Grammar",
            "explanation": "A noun is one of the main parts of speech that names a person, place, thing, or idea."
        },
        {
            "question_id": "SRC_A1B2C3D4_Q002",
            "question_text": "Pronouns are words that take the place of nouns in a sentence.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "difficulty": "easy",
            "subject": "English",
            "topic": "Grammar",
            "explanation": "True. Pronouns such as he, she, it, they are used to replace nouns."
        }
    ]
}

# Example 3: Adaptive Quiz - Before Practice
ADAPTIVE_QUIZ_INITIAL = {
    "description": "Student Alice gets their first quiz - starts at medium difficulty",
    "endpoint": "GET /api/quiz",
    "request": """
curl "http://localhost:8000/api/quiz?student_id=alice&limit=3"
    """,
    "note": "First request for alice - adaptive difficulty defaults to 'medium'"
}

# Example 4: Submit Answer - Correct
SUBMIT_CORRECT_ANSWER = {
    "description": "Student Alice answers correctly - difficulty may increase after 2 correct",
    "endpoint": "POST /api/submit-answer",
    "request": """
curl -X POST http://localhost:8000/api/submit-answer \\
  -H "Content-Type: application/json" \\
  -d '{
    "student_id": "alice",
    "question_id": "SRC_A1B2C3D4_Q001",
    "selected_answer": "A word that represents a person, place, or thing",
    "time_spent_seconds": 45
  }'
    """,
    "response": {
        "is_correct": True,
        "correct_answer": "A word that represents a person, place, or thing",
        "explanation": "A noun is one of the main parts of speech...",
        "current_difficulty": "medium",
        "accuracy_percentage": 100.0
    }
}

# Example 5: Submit Answer - Incorrect
SUBMIT_INCORRECT_ANSWER = {
    "description": "Student Bob answers incorrectly - difficulty decreases after 2 incorrect",
    "endpoint": "POST /api/submit-answer",
    "request": """
curl -X POST http://localhost:8000/api/submit-answer \\
  -H "Content-Type: application/json" \\
  -d '{
    "student_id": "bob",
    "question_id": "SRC_A1B2C3D4_Q003",
    "selected_answer": "Wrong answer",
    "time_spent_seconds": 20
  }'
    """,
    "response": {
        "is_correct": False,
        "correct_answer": "adjective",
        "explanation": "Adjectives modify or describe nouns in sentences.",
        "current_difficulty": "medium",
        "accuracy_percentage": 50.0
    }
}

# Example 6: Student Progress
GET_PROGRESS_EXAMPLE = {
    "description": "Check Alice's learning progress and current difficulty level",
    "endpoint": "GET /api/student-progress/{student_id}",
    "request": """
curl http://localhost:8000/api/student-progress/alice
    """,
    "response": {
        "student_id": "alice",
        "current_difficulty": "hard",
        "total_questions_answered": 25,
        "correct_answers": 22,
        "incorrect_answers": 3,
        "accuracy_percentage": 88.0,
        "consecutive_correct": 4,
        "consecutive_incorrect": 0,
        "last_activity": "2024-03-14T15:30:00"
    }
}

# Example 7: Comprehensive Learning Session
COMPREHENSIVE_SESSION = {
    "description": "Complete learning session flow",
    "steps": [
        {
            "step": 1,
            "description": "Upload educational PDF",
            "request": "POST /api/ingest",
            "note": "Teacher uploads lesson material"
        },
        {
            "step": 2,
            "description": "Check ingestion status",
            "request": "GET /api/ingest/status/{source_id}",
            "note": "Verify questions were generated"
        },
        {
            "step": 3,
            "description": "Student begins quiz session",
            "request": "GET /api/quiz?student_id=alice&limit=5",
            "note": "Gets 5 questions at their current level"
        },
        {
            "step": 4,
            "description": "Student submits first answer",
            "request": "POST /api/submit-answer",
            "note": "Gets feedback on answer"
        },
        {
            "step": 5,
            "description": "Student requests next question",
            "request": "GET /api/quiz?student_id=alice&limit=1",
            "note": "Difficulty may have adjusted based on previous answer"
        },
        {
            "step": 6,
            "description": "Check progress",
            "request": "GET /api/student-progress/alice",
            "note": "See updated accuracy and difficulty"
        }
    ]
}

# Example 8: Filtering Questions by Subject
GET_BY_SUBJECT_EXAMPLE = {
    "description": "Retrieve all easy mathematics questions",
    "endpoint": "GET /api/quiz/by-subject/{subject}",
    "request": """
curl "http://localhost:8000/api/quiz/by-subject/Math?difficulty=easy&limit=5"
    """,
    "note": "Useful for targeted practice sessions"
}

# Example 9: Filtering Questions by Topic
GET_BY_TOPIC_EXAMPLE = {
    "description": "Retrieve medium-difficulty 'Shapes' questions",
    "endpoint": "GET /api/quiz/by-topic/{topic}",
    "request": """
curl "http://localhost:8000/api/quiz/by-topic/Shapes?difficulty=medium&limit=3"
    """,
    "note": "Useful for focused learning on specific topics"
}


# Python Integration Example
PYTHON_INTEGRATION_EXAMPLE = """
# Python script to interact with the Quiz Engine API

import requests
import json

BASE_URL = "http://localhost:8000"

class QuizEngineClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def ingest_pdf(self, pdf_file_path):
        \"\"\"Upload a PDF file for ingestion\"\"\"
        with open(pdf_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'generate_quizzes': True,
                'questions_per_chunk': 3
            }
            response = requests.post(
                f"{self.base_url}/api/ingest",
                files=files,
                data=data
            )
        return response.json()
    
    def get_quiz(self, student_id, limit=5, topic=None, difficulty=None):
        \"\"\"Get quiz questions for a student\"\"\"
        params = {
            'student_id': student_id,
            'limit': limit,
        }
        if topic:
            params['topic'] = topic
        if difficulty:
            params['difficulty'] = difficulty
        
        response = requests.get(
            f"{self.base_url}/api/quiz",
            params=params
        )
        return response.json()
    
    def submit_answer(self, student_id, question_id, selected_answer, time_spent=None):
        \"\"\"Submit student answer\"\"\"
        payload = {
            'student_id': student_id,
            'question_id': question_id,
            'selected_answer': selected_answer,
        }
        if time_spent is not None:
            payload['time_spent_seconds'] = time_spent
        
        response = requests.post(
            f"{self.base_url}/api/submit-answer",
            json=payload
        )
        return response.json()
    
    def get_progress(self, student_id):
        \"\"\"Get student progress\"\"\"
        response = requests.get(
            f"{self.base_url}/api/student-progress/{student_id}"
        )
        return response.json()


# Usage example
if __name__ == "__main__":
    client = QuizEngineClient()
    
    # 1. Ingest PDF
    # result = client.ingest_pdf("path/to/educational_material.pdf")
    # print(f"Ingestion Result: {result}")
    
    # 2. Get quiz for student
    questions = client.get_quiz(
        student_id="alice",
        limit=3,
        topic="Grammar"
    )
    print(f"Quiz Questions: {json.dumps(questions, indent=2)}")
    
    # 3. Submit answer
    if questions:
        q = questions[0]
        feedback = client.submit_answer(
            student_id="alice",
            question_id=q['question_id'],
            selected_answer="Sample Answer",
            time_spent=45
        )
        print(f"Answer Feedback: {json.dumps(feedback, indent=2)}")
    
    # 4. Check progress
    progress = client.get_progress("alice")
    print(f"Student Progress: {json.dumps(progress, indent=2)}")
"""


# JavaScript/Node.js Integration Example
JAVASCRIPT_INTEGRATION_EXAMPLE = """
// JavaScript fetch API example

const BASE_URL = "http://localhost:8000";

class QuizEngineClient {
    constructor(baseUrl = BASE_URL) {
        this.baseUrl = baseUrl;
    }
    
    async ingestPDF(pdfFile) {
        const formData = new FormData();
        formData.append('file', pdfFile);
        formData.append('generate_quizzes', true);
        formData.append('questions_per_chunk', 3);
        
        const response = await fetch(`${this.baseUrl}/api/ingest`, {
            method: 'POST',
            body: formData
        });
        return await response.json();
    }
    
    async getQuiz(studentId, limit = 5, topic = null, difficulty = null) {
        const params = new URLSearchParams({
            student_id: studentId,
            limit: limit
        });
        
        if (topic) params.append('topic', topic);
        if (difficulty) params.append('difficulty', difficulty);
        
        const response = await fetch(
            `${this.baseUrl}/api/quiz?${params.toString()}`
        );
        return await response.json();
    }
    
    async submitAnswer(studentId, questionId, selectedAnswer, timeSpent = null) {
        const payload = {
            student_id: studentId,
            question_id: questionId,
            selected_answer: selectedAnswer
        };
        
        if (timeSpent !== null) {
            payload.time_spent_seconds = timeSpent;
        }
        
        const response = await fetch(`${this.baseUrl}/api/submit-answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        return await response.json();
    }
    
    async getProgress(studentId) {
        const response = await fetch(
            `${this.baseUrl}/api/student-progress/${studentId}`
        );
        return await response.json();
    }
}

// Usage
const client = new QuizEngineClient();

// Get quiz questions
client.getQuiz('alice', 5, 'Grammar', 'medium')
    .then(questions => {
        console.log('Quiz Questions:', questions);
        
        // Submit answer to first question
        if (questions.length > 0) {
            const q = questions[0];
            return client.submitAnswer(
                'alice',
                q.question_id,
                'Answer text',
                45
            );
        }
    })
    .then(feedback => {
        console.log('Feedback:', feedback);
        return client.getProgress('alice');
    })
    .then(progress => {
        console.log('Progress:', progress);
    })
    .catch(error => console.error('Error:', error));
"""


if __name__ == "__main__":
    print("=== Quiz Engine Examples ===")
    print()
    print("1. PDF Ingestion:")
    print(json.dumps(INGEST_REQUEST_EXAMPLE, indent=2))
    print()
    print("2. Get Quiz Questions:")
    print(json.dumps(GET_QUIZ_EXAMPLE, indent=2))
    print()
    print("3. Python Integration:")
    print(PYTHON_INTEGRATION_EXAMPLE)
    print()
    print("4. JavaScript Integration:")
    print(JAVASCRIPT_INTEGRATION_EXAMPLE)
