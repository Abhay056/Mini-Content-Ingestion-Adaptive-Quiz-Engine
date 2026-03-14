# Troubleshooting & FAQ Guide

## Frequently Asked Questions

### General Questions

**Q: What Python version is required?**
A: Python 3.10 or higher. Check with `python --version`

**Q: Can I use SQLite instead of PostgreSQL?**
A: Yes, change `DATABASE_URL` in `.env` to `sqlite:///./quiz_engine.db`, but PostgreSQL is recommended for production.

**Q: Do I need to have all three PDF files?**
A: No. The system works with any PDFs. The three provided PDFs are examples. You can upload one or all of them.

**Q: How long does PDF processing take?**
A: Depends on PDF size. Typical: 1-2 minutes for a 10-page document with quiz generation.

**Q: Can I regenerate quizzes without re-uploading the PDF?**
A: Currently no, but this could be added as a feature via `POST /api/generate-quiz/{source_id}`

---

## Installation & Setup Troubleshooting

### ❌ Problem: "Python is not recognized as an internal or external command"

**Cause**: Python not in system PATH or not installed

**Solutions**:
1. Reinstall Python, ensuring "Add Python to PATH" is checked
2. Use full path: `C:\Python310\python.exe --version`
3. Use Windows PowerShell instead of Command Prompt

---

### ❌ Problem: "Cannot activate virtual environment"

**Cause**: Virtual environment not created properly

**Windows**:
```bash
# Try different activation script
venv\Scripts\activate.bat
# or
venv\Scripts\activate.ps1

# If still fails, recreate venv
rmdir /s venv
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux**:
```bash
# Check permission
chmod +x venv/bin/activate
source venv/bin/activate
```

---

### ❌ Problem: "pip: command not found"

**Cause**: pip not available or virtual environment not activated

**Solution**:
```bash
# Don't use virtual environment, install globally
python -m pip install --upgrade pip

# Then activate venv and try again
venv\Scripts\activate
pip install -r requirements.txt
```

---

### ❌ Problem: "No module named fastapi/sqlalchemy/etc"

**Cause**: Dependencies not installed in active environment

**Solution**:
```bash
# Verify virtual environment is active (should see (venv) prefix)
echo %PATH%  # Windows
echo $PATH   # macOS/Linux

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
pip list | grep -i fastapi
```

---

## Database Troubleshooting

### ❌ Problem: "could not translate host name to address"

**Cause**: PostgreSQL server not running

**Windows**:
```bash
# Check if PostgreSQL service is running
# Open Services app (services.msc)
# Look for "postgresql-x64-XX"
# If not running, right-click and click Start
```

**macOS**:
```bash
# Check if PostgreSQL is running
brew services list

# Start if not running
brew services start postgresql

# Or use PostgreSQL.app if installed
```

**Linux**:
```bash
# Check status
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql
```

---

### ❌ Problem: "FATAL: password authentication failed"

**Cause**: Wrong PostgreSQL password

**Solution**:
1. Verify password in `.env` matches PostgreSQL installation
2. Reset PostgreSQL password:

```bash
# Windows (run as Administrator)
psql -U postgres
ALTER USER postgres PASSWORD 'new_password';

# macOS/Linux
sudo -u postgres psql
ALTER USER postgres PASSWORD 'new_password';
```

Update `.env` with new password.

---

### ❌ Problem: "database quiz_engine does not exist"

**Cause**: Database not created

**Solution**:
```bash
# Create database
psql -U postgres
CREATE DATABASE quiz_engine;
\q

# Or using system command
createdb quiz_engine

# Verify
psql -l | grep quiz_engine
```

---

### ❌ Problem: "SQLAlchemy can't find tables"

**Cause**: Tables not created on startup

**Solution**:
```bash
# Ensure app/database.py init_db() is called
# Should happen automatically on first startup

# Or manually initialize
python -c "from app.database import init_db; init_db()"

# Verify tables created
psql -U postgres -d quiz_engine
\dt  # Lists tables
```

---

## Application Runtime Troubleshooting

### ❌ Problem: "Uvicorn not found"

**Cause**: Dependencies not installed properly

**Solution**:
```bash
# Activate virtual environment
venv\Scripts\activate

# Reinstall with specific version
pip install uvicorn==0.24.0
pip install -r requirements.txt

# or use python -m
python -m uvicorn app.main:app --reload
```

---

### ❌ Problem: "ModuleNotFoundError: No module named 'app'"

**Cause**: Not running from correct directory

**Solution**:
```bash
# Ensure you're in the project root
pwd  # macOS/Linux
cd   # Windows

# Should show: Mini Content Ingestion and Adaptive Quiz Engine

# Then run
python -m uvicorn app.main:app --reload
```

---

### ❌ Problem: "Address already in use" (Port 8000)

**Cause**: Another process using port 8000

**Solutions**:

```bash
# Windows - find process
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID 1234 /F

# Or use different port
python -m uvicorn app.main:app --port 8001
```

```bash
# macOS/Linux - find process
lsof -i :8000

# Kill process (replace PID)
kill -9 1234

# Or use different port
python -m uvicorn app.main:app --port 8001
```

---

### ❌ Problem: "No changes detected in 'migrations'" (Alembic)

**Cause**: Database schema already exists

**Solution**: This message is informational. If you see it on first run, tables exist and were created by SQLAlchemy.

---

## File Upload & PDF Troubleshooting

### ❌ Problem: PDF upload fails with "Only PDF files are accepted"

**Cause**: File extension not .pdf

**Solution**:
- Ensure file ends with `.pdf`
- Check file isn't corrupted
- Try with one of the provided sample PDFs first

---

### ❌ Problem: PDF upload fails with "File size exceeds limit"

**Cause**: PDF larger than `MAX_PDF_SIZE_MB` (default 50MB)

**Solutions**:
1. Use smaller PDF (split large PDFs into parts)
2. Increase limit in `.env`:
```env
MAX_PDF_SIZE_MB=100
```

---

### ❌ Problem: "No text extracted from PDF"

**Cause**: PDF might be image-based (scanned), not text-based

**Solutions**:
1. Use PDF with embedded text
2. Use OCR tool first to convert image PDF to text
3. Check with: `pdftotext file.pdf` (if pdftotext installed)

---

### ❌ Problem: PDFs directory doesn't exist

**Cause**: `/pdfs` directory not created

**Solution**:
```bash
# Create directory
mkdir pdfs

# Or it creates automatically on first upload
# Just try uploading again
```

---

## LLM/Gemini API Troubleshooting

### ❌ Problem: "APIError: 403 Forbidden"

**Cause**: Invalid Gemini API key or insufficient permissions

**Solutions**:
1. Verify API key in `.env`:
```bash
python -c "from app.config import settings; print(settings.GEMINI_API_KEY)"
```

2. Get new API key:
   - Visit: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy and paste into `.env`

3. Check Google Cloud permissions

---

### ❌ Problem: "APIError: 429 Too Many Requests"

**Cause**: Rate limiting - too many calls to Gemini API

**Solutions**:
1. Reduce questions per chunk in ingestion
2. Wait a few minutes before retry
3. Consider implementing request queue (future feature)

---

### ❌ Problem: "JSON decode error" from Gemini response

**Cause**: Gemini returned invalid format

**Solution**:
- System has fallback to dummy questions
- Check logs for error detail
- Try again - may be transient issue
- If persistent, Gemini API might be down

---

### ❌ Problem: Quiz questions are dummy questions

**Cause**: Gemini API not configured or unavailable

**Solution**:
1. Verify `GEMINI_API_KEY` in `.env`
2. Check API key is valid (try new key from makersuite.google.com)
3. Check network connectivity
4. Check if Gemini API is in maintenance

**Note**: Dummy questions allow testing without Gemini API

---

## Testing Troubleshooting

### ❌ Problem: Tests fail with "No module named 'app'"

**Cause**: Not running from correct directory or environment

**Solution**:
```bash
# Ensure in project root
# Activate virtual environment
venv\Scripts\activate

# Run pytest explicitly
python -m pytest tests/ -v
```

---

### ❌ Problem: "FAILED - fixture 'db' not found"

**Cause**: conftest.py not found or not imported

**Solution**:
```bash
# Verify conftest.py exists
ls tests/conftest.py

# Ensure __init__.py exists in tests/
touch tests/__init__.py

# Run tests again
pytest tests/ -v
```

---

### ❌ Problem: Tests timeout or hang

**Cause**: Database connection issue or infinite loop

**Solution**:
```bash
# Run with timeout
pytest tests/ -v --timeout=10

# Run specific test with verbose output
pytest tests/test_api.py::test_health_check -v -s

# Check database isn't locked
psql -U postgres -d quiz_engine
\q
```

---

## API Testing Troubleshooting

### ❌ Problem: Swagger UI shows "OpenAPI schema error"

**Cause**: API not running or schema generation failed

**Solution**:
1. Verify API is running on port 8000
2. Check application logs for errors
3. Restart application

---

### ❌ Problem: curl command fails "Failed to connect"

**Cause**: API not running on that port/host

**Solution**:
```bash
# Check if API is running
curl http://localhost:8000/health

# If fails, start API
python -m uvicorn app.main:app --reload

# Try again
curl http://localhost:8000/health
```

---

### ❌ Problem: POST request fails with "422 Unprocessable Entity"

**Cause**: Request body doesn't match schema

**Solution**:
1. Check request body matches expected schema
2. Verify Content-Type header: `Content-Type: application/json`
3. Validate JSON syntax
4. Check Swagger docs at http://localhost:8000/docs for schema

Example:
```bash
# WRONG - missing required field
curl -X POST http://localhost:8000/api/submit-answer \
  -H "Content-Type: application/json" \
  -d '{"student_id": "test"}'

# RIGHT
curl -X POST http://localhost:8000/api/submit-answer \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test",
    "question_id": "Q001",
    "selected_answer": "answer"
  }'
```

---

## Performance Troubleshooting

### ❌ Problem: Slow PDF processing

**Cause**: Large PDFs or slow LLM API

**Solutions**:
1. Try smaller PDFs first
2. Reduce `questions_per_chunk` in ingestion request
3. Check network latency to Gemini API
4. Process in background (future feature)

---

### ❌ Problem: Slow API response times

**Cause**: Database not indexed, too many results, or heavy processing

**Solutions**:
1. Check database indexes
2. Limit results with `limit` parameter
3. Filter by specific topic/subject
4. Check database connection

---

### ❌ Problem: High memory usage

**Cause**: Large chunks loaded in memory

**Solutions**:
1. Reduce `CHUNK_SIZE` in config
2. Process PDFs in batches
3. Implement pagination (future)

---

## Logging & Debugging

### ❌ Problem: "Can't see application logs"

**Solution**:
```bash
# Run with explicit log level
python -m uvicorn app.main:app --log-level debug

# Or set in .env
LOG_LEVEL=DEBUG

# Check logs are written to console
```

---

### ❌ Problem: "Need more detailed error information"

**Solution**:
```bash
# Enable debug mode
# In .env
DEBUG=True

# Restart application - will show more details
# Check application output for stack traces
```

---

## Getting Help

### If you can't find your issue here:

1. **Check existing documentation**:
   - README.md - General overview
   - ARCHITECTURE.md - System design
   - API_REFERENCE.md - API details

2. **Check application logs**:
   - Terminal output showing stack traces
   - Database error messages
   - API response error details

3. **Check error message carefully**:
   - Often contains clue to solution
   - Search error in relevant documentation

4. **Try minimal reproduction**:
   - Test with simple example
   - Use provided sample PDFs
   - Check with curl before Postman/client code

5. **Verify prerequisites**:
   - Python version
   - PostgreSQL running
   - Virtual environment activated
   - Dependencies installed

---

## System Health Check

Use this script to verify all components are working:

```bash
# 1. Check Python
python --version  # Should be 3.10+

# 2. Check virtual environment
which python  # Should show path with venv

# 3. Check PostgreSQL
psql --version  # Should be 12+

# 4. Check database connection
psql -U postgres -d quiz_engine -c "SELECT 1;"

# 5. Check API starts
python -m uvicorn app.main:app --port 8001
# Should see "Uvicorn running on http://0.0.0.0:8001"

# 6. Test health endpoint
curl http://localhost:8001/health
# Should return JSON with "status": "healthy"

# 7. Check Gemini API
python -c "from app.config import settings; print('API Key configured' if settings.GEMINI_API_KEY else 'API Key missing')"
```

---

**Last Updated**: March 2024  
**Version**: 1.0.0

