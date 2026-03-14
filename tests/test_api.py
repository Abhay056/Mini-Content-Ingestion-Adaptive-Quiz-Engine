"""Tests for API endpoints"""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_get_quiz_empty_db(client):
    """Test getting quiz from empty database"""
    response = client.get("/api/quiz")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_student_progress_creates_new(client, test_student_id):
    """Test that getting student progress creates new record if not exists"""
    response = client.get(f"/api/student-progress/{test_student_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == test_student_id
    assert data["current_difficulty"] == "medium"
    assert data["total_questions_answered"] == 0


def test_submit_answer_question_not_found(client, test_student_id):
    """Test submitting answer for non-existent question"""
    response = client.post("/api/submit-answer", json={
        "student_id": test_student_id,
        "question_id": "NON_EXISTENT",
        "selected_answer": "Test Answer",
        "time_spent_seconds": 30
    })
    assert response.status_code == 404


# Integration test - would need actual test data
@pytest.mark.asyncio
async def test_pdf_ingestion_endpoint():
    """Integration test for PDF ingestion (requires actual PDF file)"""
    # This would test the actual /api/ingest endpoint
    # Requires a test PDF file
    pass
