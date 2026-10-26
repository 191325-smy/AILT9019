@echo off
setlocal
cd /d "%~dp0"
set "DEMO_PYTHON=python"
if exist ".venv\Scripts\python.exe" set "DEMO_PYTHON=%CD%\.venv\Scripts\python.exe"
"%DEMO_PYTHON%" -c "import fastapi, uvicorn, pwdlib" 2>nul
if errorlevel 1 (
    "%DEMO_PYTHON%" -m pip install -r backend\requirements.txt
    if errorlevel 1 exit /b 1
)
if not exist "matching\ailt9019.db" (
    "%DEMO_PYTHON%" matching\seed.py
    if errorlevel 1 exit /b 1
)
echo Backend: http://localhost:8000/docs
"%DEMO_PYTHON%" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
