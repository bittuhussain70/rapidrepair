#!/bin/bash
# RapidRepair Multi-Service Launcher
# Runs Flask app and Node.js worker in parallel

set -e

echo "🚀 Starting RapidRepair Services..."

# Function to handle cleanup
cleanup() {
    echo "Shutting down services..."
    kill $FLASK_PID $WORKER_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Flask app
echo "Starting Flask app on port 5000..."
python app.py > server.out.log 2> server.err.log &
FLASK_PID=$!
echo "Flask app PID: $FLASK_PID"

# Wait for Flask to start
sleep 2

# Install worker dependencies if needed
if [ ! -d "worker/node_modules" ]; then
    echo "Installing Node.js dependencies..."
    cd worker
    npm install
    cd ..
fi

# Start Node.js worker
echo "Starting Node.js worker on port 3000..."
cd worker
npm start > worker.out.log 2> worker.err.log &
WORKER_PID=$!
echo "Worker PID: $WORKER_PID"
cd ..

echo ""
echo "✅ Services started successfully!"
echo "📊 Flask app: http://127.0.0.1:5000"
echo "⚙️  Worker API: http://127.0.0.1:3000/api/worker/health"
echo "📈 Analytics: http://127.0.0.1:3000/api/worker/analytics"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep script running
wait
