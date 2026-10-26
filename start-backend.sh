#!/bin/bash
# Start the FastAPI backend server

echo "=================================="
echo "AILT9019 Teammate Matcher - Backend"
echo "=================================="
echo ""

# Check if database exists, if not seed it
if [ ! -f "matching/ailt9019.db" ]; then
    echo "Database not found. Seeding..."
    cd matching
    python seed.py
    cd ..
    echo "Database seeded successfully!"
    echo ""
fi

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing backend dependencies..."
    pip install -r backend/requirements.txt
    echo ""
fi

# Start the server
echo "Starting backend server at http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
