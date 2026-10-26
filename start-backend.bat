@echo off
REM Start the FastAPI backend server

echo ==================================
echo AILT9019 Teammate Matcher - Backend
echo ==================================
echo.

REM Check if database exists, if not seed it
if not exist "matching\ailt9019.db" (
    echo Database not found. Seeding...
    cd matching
    python seed.py
    cd ..
    echo Database seeded successfully!
    echo.
)

REM Install dependencies if needed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing backend dependencies...
    pip install -r backend\requirements.txt
    echo.
)

REM Start the server
echo Starting backend server at http://localhost:8000
echo Press Ctrl+C to stop
echo.

cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
