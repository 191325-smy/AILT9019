@echo off
setlocal
cd /d "%~dp0"
set "DEMO_PYTHON=python"
if exist ".venv\Scripts\python.exe" set "DEMO_PYTHON=%CD%\.venv\Scripts\python.exe"
echo Open http://localhost:8001/index.html
"%DEMO_PYTHON%" -m http.server 8001 --bind 127.0.0.1 --directory ui
