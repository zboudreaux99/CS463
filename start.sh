#!/bin/bash
echo "Installing Python dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Running backend tests..."
python3 -m pytest test_backend.py -v || { echo "Backend tests failed"; exit 1; }

echo "Running frontend tests..."
python3 -m pytest test_frontend.py -v || { echo "Frontend tests failed"; exit 1; }

echo "Starting backend..."
# python3 backend.py &
python3 backend.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID $BACKEND_PID"

echo "Starting frontend..."
# python3 frontend.py &
python3 frontend.py > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID $FRONTEND_PID"
echo "All services started successfully."

# Handle Ctrl+C to stop frontend and backend
trap "echo 'Stopping frontend and backend...'; kill $FRONTEND_PID; kill $BACKEND_PID; exit 0" SIGINT

# Keep the script running so both processes stay alive
wait
