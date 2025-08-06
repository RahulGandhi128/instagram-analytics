#!/bin/bash
echo "Starting Instagram Analytics Development Environment..."

echo ""
echo "Setting up Backend..."
cd backend

echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Starting Flask server in background..."
python app.py &
BACKEND_PID=$!

echo ""
echo "Setting up Frontend..."
cd ../frontend

echo "Installing Node dependencies..."
if [ ! -d "node_modules" ]; then
    npm install
fi

echo "Starting React development server..."
npm start &
FRONTEND_PID=$!

cd ..

echo ""
echo "================================"
echo "   Development Environment Ready"
echo "================================"
echo ""
echo "Backend (Flask): http://localhost:5000"
echo "Frontend (React): http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Wait for user to stop
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
