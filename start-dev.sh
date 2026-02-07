#!/bin/bash
# Development start script
# Starts both backend and frontend in development mode

echo "Starting Stratify AI Development Environment"
echo "=============================================="

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "Error: backend/.env not found!"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Function to kill processes on exit
cleanup() {
    echo "Shutting down..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup INT TERM

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate 2>/dev/null || {
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}

cd app
python main.py &
BACKEND_PID=$!
cd ../..

echo "Backend started (PID: $BACKEND_PID)"
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd frontend

if [ ! -d node_modules ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ..

echo "Frontend started (PID: $FRONTEND_PID)"
echo "UI: http://localhost:3000"

echo ""
echo "Development servers running!"
echo "Press Ctrl+C to stop"

# Wait for both processes
wait
