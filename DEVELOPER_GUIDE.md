# Developer Quick Reference

## Common Commands

### Running the Application
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Start development server (with auto-reload)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start production server (no auto-reload)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Database Management
```bash
# View database
psql -U postgres -d quiz_engine

# Create fresh database
dropdb quiz_engine
createdb quiz_engine

# Run application (auto-initializes tables)
python -m uvicorn app.main:app --reload
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run tests matching pattern
pytest tests/ -k "health" -v
```

### Code Quality
```bash
# Format code (install black first: pip install black)
black app/ tests/

# Lint code (install flake8 first: pip install flake8)
flake8 app/ --max-line-length=100

# Type checking (install mypy first: pip install mypy)
mypy app/ --ignore-missing-imports
```

### Dependencies
```bash
# Update dependencies file
pip freeze > requirements.txt

# Install specific version
pip install package_name==1.2.3

# List installed packages
pip list

# Upgrade all packages
pip install --upgrade -r requirements.txt
```

---

## Project File Reference

### Core Application Files
| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI application entry point |
| `app/config.py` | Configuration from environment |
| `app/database.py` | Database connection and session |
| `app/utils.py` | Utility functions for initialization |

### Models
| File | Contains |
|------|----------|
| `app/models/content.py` | Source, ContentChunk models |
| `app/models/quiz.py` | Question, Answer, Progress models |

### Services
| File | Purpose |
|------|---------|
| `app/services/__init__.py` | PDF extraction service |
| `app/services/quiz_generation.py` | Gemini LLM integration |
| `app/services/adaptive_difficulty.py` | Adaptive logic |
| `app/services/ingestion.py` | Ingestion orchestration |

### API Routes
| File | Endpoints |
|------|-----------|
| `app/api/ingestion.py` | POST /api/ingest, GET /api/ingest/status |
| `app/api/quiz.py` | GET /api/quiz, POST /api/submit-answer, GET /api/student-progress |

### Schemas
| File | Contains |
|------|----------|
| `app/schemas/__init__.py` | All Pydantic request/response schemas |

---

## Adding New Features

### Adding a New API Endpoint

1. **Create route in `app/api/new_feature.py`**:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/api", tags=["new_feature"])

@router.get("/new-endpoint")
async def new_endpoint(db: Session = Depends(get_db)):
    return {"message": "Success"}
```

2. **Include router in `app/main.py`**:
```python
from app.api.new_feature import router as new_router
app.include_router(new_router)
```

3. **Add schema in `app/schemas/__init__.py`**:
```python
class NewRequestSchema(BaseModel):
    field1: str
    field2: int
```

### Adding a New Database Model

1. **Create model in `app/models/new_model.py`**:
```python
from sqlalchemy import Column, String, Integer
from app.database import Base

class NewModel(Base):
    __tablename__ = "new_model_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

2. **Import in `app/models/__init__.py`**:
```python
from app.models.new_model import NewModel
```

3. **Schema in `app/schemas/__init__.py`**:
```python
class NewModelSchema(BaseModel):
    name: str
    
    class Config:
        from_attributes = True
```

### Adding a New Service

1. **Create `app/services/new_service.py`**:
```python
class NewService:
    @staticmethod
    def do_something(param: str) -> dict:
        return {"result": param}
```

2. **Use in routes**:
```python
from app.services.new_service import NewService

result = NewService.do_something("test")
```

---

## Debugging Tips

### Enable Debug Logging
```python
# In app/config.py or during development
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Query Logging
```env
# In .env
DEBUG=True
# SQLAlchemy will log all queries
```

### Test API Endpoint Directly
```bash
# Using curl
curl -X GET "http://localhost:8000/api/quiz?limit=1"

# Using Python requests
import requests
response = requests.get("http://localhost:8000/api/quiz?limit=1")
print(response.json())
```

### Check Database State
```bash
# Connect to database
psql -U postgres -d quiz_engine

# View tables
\dt

# Query data
SELECT * FROM sources;
SELECT * FROM student_progress;

# Exit
\q
```

---

## Common Issues & Solutions

### Issue: "PostgreSQL connection failed"
```bash
# Check if PostgreSQL is running
# Windows: Services app
# Check DATABASE_URL format
# Verify username and password
```

### Issue: "Module not found"
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"
```bash
# Use different port
python -m uvicorn app.main:app --port 8001

# Or kill process using port 8000
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000 | grep LISTEN
```

### Issue: "Gemini API error 403"
```bash
# Verify API key in .env
# Check Google Cloud permissions
# Create new API key if needed
```

---

## Environment Variables Glossary

| Variable | Type | Purpose |
|----------|------|---------|
| `DATABASE_URL` | string | PostgreSQL connection string |
| `GEMINI_API_KEY` | string | Google Gemini API key |
| `APP_ENV` | string | development or production |
| `DEBUG` | boolean | Enable/disable debug mode |
| `LOG_LEVEL` | string | DEBUG, INFO, WARNING, ERROR |
| `MAX_PDF_SIZE_MB` | integer | Max PDF file size limit |
| `PDF_UPLOAD_DIR` | string | Directory for uploaded PDFs |
| `TEMPERATURE` | float | LLM creativity (0-1) |
| `MAX_TOKENS` | integer | Max LLM response length |

---

## Performance Optimization Tips

### Database
- Add indexes on frequently queried columns
- Use connection pooling (configured in database.py)
- Profile slow queries with EXPLAIN ANALYZE

### API
- Use caching for frequently accessed questions (future)
- Implement pagination for large result sets
- Optimize N+1 queries by using proper joins

### LLM
- Batch question generation when possible
- Cache responses for identical content
- Use asynchronous processing for long operations

---

## Git Workflow

### Before Committing
```bash
# Check status
git status

# Ensure .env is not staged
# Add files
git add .

# Commit with message
git commit -m "Add feature: description"

# Push to remote
git push origin main
```

### Branching Strategy
```bash
# Feature branch
git checkout -b feature/feature-name
# ... make changes ...
git push origin feature/feature-name
# Create pull request

# Hotfix branch
git checkout -b hotfix/bug-fix
# ... fix bug ...
git push origin hotfix/bug-fix
```

---

## Useful Links

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Pytest Docs**: https://docs.pytest.org/
- **Google Gemini API**: https://https://makersuite.google.com/

---

## Contact & Support

For issues or questions:
1. Check documentation files
2. Review API examples in EXAMPLES.md
3. Check test files for usage patterns
4. Review error logs in application output

---

**Last Updated**: March 2024
**Version**: 1.0.0

