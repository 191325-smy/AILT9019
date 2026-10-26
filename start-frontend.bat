@echo off
REM Start the frontend UI server

echo ==================================
echo AILT9019 Teammate Matcher - Frontend
echo ==================================
echo.
echo Starting frontend server at http://localhost:8001
echo Open your browser and go to: http://localhost:8001
echo Press Ctrl+C to stop
echo.

cd ui
python -m http.server 8001
