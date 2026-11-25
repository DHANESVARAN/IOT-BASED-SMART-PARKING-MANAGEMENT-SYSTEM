#!/bin/bash

# Define the absolute path to your project
PROJECT_DIR="/run/media/dhanesh/Secondary Drive/PROJECT FILES/SSS - Project"

echo "Initializing Walmart Parking Simulator Stack..."

# 1. Start the Flask Backend API in the background
echo "[1/3] Starting Backend API..."
cd "$PROJECT_DIR/backend"
source ../venv/bin/activate
python app.py > backend.log 2>&1 &
BACKEND_PID=$!
sleep 2 # Give the server a moment to boot

# 2. Start the IoT Simulator Engine in the background
echo "[2/3] Starting IoT Simulator..."
cd "$PROJECT_DIR"
source venv/bin/activate
python backend/simulator/engine.py > simulator.log 2>&1 &
SIM_PID=$!

# 3. Start the React Frontend (this automatically opens the browser)
echo "[3/3] Starting React UI..."
cd "$PROJECT_DIR/frontend"
npm start > frontend.log 2>&1 &
REACT_PID=$!

echo "========================================================"
echo "✅ All services are now running in the background!"
echo "🌐 The React dashboard is opening at http://localhost:3000"
echo "🛑 Press [CTRL+C] in this terminal to stop all services."
echo "========================================================"

# Catch the CTRL+C signal to cleanly kill all three processes at once
trap "echo -e '\nShutting down all parking services...'; kill $BACKEND_PID $SIM_PID $REACT_PID; exit" SIGINT

# Keep the script alive while the background processes run
wait
