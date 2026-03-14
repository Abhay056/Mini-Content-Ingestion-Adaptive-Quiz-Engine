# Setup and Installation Guide

## Prerequisites Verification

Before starting, ensure you have:

### Required Software
- ✓ Python 3.10 or higher
- ✓ PostgreSQL 12 or higher
- ✓ Git (for version control)
- ✓ A text editor or IDE (VS Code, PyCharm, etc.)

### Required Accounts
- ✓ Google Cloud account (for Gemini API key)

### Check Python Version
```bash
python --version
# Should output: Python 3.10.x or higher
```

### Check PostgreSQL Installation
```bash
psql --version
# Should output: psql (PostgreSQL) 12.x or higher
```

---

## Step-by-Step Installation

### Step 1: Clone or Download Repository

**Option A: Using Git**
```bash
git clone <repository-url>
cd "Mini Content Ingestion and Adaptive Quiz Engine"
```

**Option B: Download ZIP**
- Download as ZIP from repository
- Extract to desired location
- Open terminal/cmd in the extracted folder

### Step 2: Create Python Virtual Environment

The virtual environment isolates project dependencies from system Python.

**Windows (Command Prompt or PowerShell)**:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) prefix in terminal
```

**macOS/Linux (Terminal)**:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) prefix in terminal
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip (recommended)
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**Expected Output**:
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 sqlalchemy-2.0.23 ...
```

### Step 4: Set Up PostgreSQL Database

#### Option A: Using PostgreSQL Command Line

**Windows** (assuming PostgreSQL is installed):
```bash
# Open PostgreSQL prompt (or use pgAdmin)
psql -U postgres

# Once in psql:
CREATE DATABASE quiz_engine;

# Verify
\l
# Should show quiz_engine in list

# Exit
\q
```

**macOS/Linux**:
```bash
# Create database
createdb quiz_engine

# Verify (list all databases)
psql -l
```

#### Option B: Using pgAdmin (GUI)

1. Open pgAdmin (installed with PostgreSQL)
2. Connect to your local server
3. Right-click "Databases" → Create → Database
4. Enter name: "quiz_engine"
5. Click Save

### Step 5: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Open .env in your text editor
# Windows: start .env
# macOS: open .env
# Linux: nano .env
```

**Edit the following in `.env`**:

#### Database Configuration
```env
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/quiz_engine
```

**Explanation**:
- `postgres`: Default PostgreSQL user (change if you created a different user)
- `your_password`: Password you set during PostgreSQL installation
- `localhost`: Database server location (usually local)
- `5432`: Default PostgreSQL port
- `quiz_engine`: Database name you created

**Example** (if PostgreSQL password is "admin123"):
```env
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/quiz_engine
```

#### Gemini API Key Configuration

```env
GEMINI_API_KEY=your_api_key_here
```

**How to Get Gemini API Key**:

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key" or "Get API Key"
3. Select "Create API key in new project" (if first time)
4. Copy the generated API key
5. Paste into `.env` file

**Example**:
```env
GEMINI_API_KEY=AIzaSyDr1234abcd5678efgh9...
```

#### Application Settings (Optional)

```env
# Environment: development or production
APP_ENV=development

# Enable/disable debug mode
DEBUG=True

# Logging level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
```

#### PDF Processing Settings (Optional)

```env
# Maximum PDF file size in MB
MAX_PDF_SIZE_MB=50

# Directory to store uploaded PDFs
PDF_UPLOAD_DIR=./pdfs
```

**Complete `.env` Example**:
```env
# Database Configuration
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/quiz_engine

# Google Gemini API Key
GEMINI_API_KEY=AIzaSyDr1234abcd5678efgh9...

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

### Step 6: Verify Configuration

```bash
# Test database connection
python -c "from app.config import settings; print(settings.DATABASE_URL)"
# Should print your database URL

# Test Gemini API key
python -c "from app.config import settings; print('API Key set' if settings.GEMINI_API_KEY else 'API Key missing')"
# Should print: API Key set
```

---

## Running the Application

### Start the Server

```bash
# Make sure virtual environment is activated
# You should see (venv) prefix

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Initializing database...
INFO:     Application startup complete
```

### Access the Application

Open your web browser and navigate to:

- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

### Stop the Server

Press `CTRL+C` in the terminal to stop the server.

---

## Testing the API

### Method 1: Using Swagger UI (Recommended for Beginners)

1. Go to http://localhost:8000/docs
2. Find the endpoint you want to test
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. See the response

### Method 2: Using curl (Command Line)

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Upload and Ingest PDF**:
```bash
# Note: Replace "path_to_pdf" with actual PDF file path
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@path_to_pdf/sample.pdf" \
  -F "generate_quizzes=true"
```

**Get Quiz Questions**:
```bash
curl "http://localhost:8000/api/quiz?limit=3"
```

**Submit Answer**:
```bash
curl -X POST http://localhost:8000/api/submit-answer \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test_student",
    "question_id": "SRC_ABC123_Q001",
    "selected_answer": "Sample Answer",
    "time_spent_seconds": 30
  }'
```

### Method 3: Using Postman

1. Download [Postman](https://www.postman.com/downloads/)
2. Create a new request
3. Set URL: http://localhost:8000/api/quiz
4. Set method: GET
5. Add query parameters
6. Send request

---

## Running Tests

### Execute Test Suite

```bash
# Activate virtual environment first
# venv\Scripts\activate (Windows) or source venv/bin/activate (macOS/Linux)

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

**Expected Output**:
```
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_root_endpoint PASSED
tests/test_api.py::test_get_student_progress_creates_new PASSED
...
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Cause**: Dependencies not installed or wrong virtual environment

**Solution**:
```bash
# Verify virtual environment is activated
which python  # Should show path with venv in it

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "Could not connect to database"

**Cause**: PostgreSQL not running, wrong password, or incorrect DATABASE_URL

**Troubleshooting**:
```bash
# Check if PostgreSQL is running
# Windows: Services (search in Start menu)
# macOS: System Preferences → PostgreSQL
# Linux: sudo systemctl status postgresql

# Test connection directly
psql -U postgres -h localhost

# Verify DATABASE_URL format
python -c "from app.config import settings; print(settings.DATABASE_URL)"
```

### Issue: "APIError: 403 Forbidden" (Gemini API)

**Cause**: Invalid API key or insufficient permissions

**Solution**:
1. Verify API key is correct in `.env`
2. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Check if API is enabled in Google Cloud console
4. Consider creating a new API key

### Issue: "Port 8000 already in use"

**Cause**: Another application using port 8000

**Solution**:
```bash
# Use different port
python -m uvicorn app.main:app --port 8001

# Or find and kill process using port 8000
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000
```

### Issue: PDF Upload Fails

**Cause**: File size too large or invalid PDF

**Solution**:
- Check file size (max 50MB in config)
- Verify PDF is not corrupted
- Try smaller PDF file
- Check `/pdfs` directory exists

---

## Development Workflow

### Making Code Changes

1. Edit Python files in `/app` directory
2. Server automatically reloads (due to `--reload` flag)
3. Check terminal for errors
4. Test changes via http://localhost:8000/docs

### Adding Dependencies

```bash
# Install new package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt

# Note: Only commit requirements.txt, not venv folder
```

### Committing Code

```bash
# Before committing, ensure .env is NOT committed
git status  # Check that .env is not listed

# Add files
git add -A

# Commit
git commit -m "Description of changes"

# Push
git push
```

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Set `APP_ENV=production` in `.env`
- [ ] Set `DEBUG=False` in `.env`
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure CORS appropriately
- [ ] Set up database backups
- [ ] Test all endpoints thoroughly
- [ ] Set up monitoring and alerts
- [ ] Configure rate limiting
- [ ] Use environment-specific config files

---

## Next Steps

1. ✓ Installation complete
2. ✓ Database configured
3. ✓ Environment variables set
4. ✓ Server running
5. **Next**: Upload a PDF file to test the system

### Quick Start Workflow

```bash
# 1. Server running? (in first terminal)
# python -m uvicorn app.main:app --reload

# 2. Open Swagger UI
# http://localhost:8000/docs

# 3. Test ingestion
# POST /api/ingest with a PDF file

# 4. Test quiz retrieval
# GET /api/quiz?limit=3

# 5. Test answer submission
# POST /api/submit-answer
```

---

## Need Help?

Refer to the following:
- **API Details**: See [API_REFERENCE.md](API_REFERENCE.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Comprehensive Guide**: See [README.md](README.md)
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

**Last Updated**: March 2024  
**Version**: 1.0.0
