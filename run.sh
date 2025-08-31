#!/bin/bash

# InvestShield Demo Script
# This script sets up and runs the complete InvestShield application

echo "🚀 Starting InvestShield - AI-powered Investor Fraud Detection Tool"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2)
        print_success "Python $PYTHON_VERSION found"
        return 0
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        return 1
    fi
}

# Check if Node.js is installed
check_node() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
        return 0
    else
        print_error "Node.js is not installed. Please install Node.js 14 or higher."
        return 1
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_success "Backend setup completed"
    cd ..
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install npm dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    print_success "Frontend setup completed"
    cd ..
}

# Train ML models
train_models() {
    print_status "Training ML models..."
    
    cd models
    python3 train_model.py
    
    print_success "Model training completed"
    cd ..
}

# Start backend server
start_backend() {
    print_status "Starting backend server..."
    
    cd backend
    source venv/bin/activate
    
    # Start the server in background
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    print_success "Backend server started on http://localhost:8000"
    print_status "Backend logs: backend.log"
    
    cd ..
}

# Start frontend server
start_frontend() {
    print_status "Starting frontend server..."
    
    cd frontend
    
    # Start the React development server in background
    nohup npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    print_success "Frontend server started on http://localhost:3000"
    print_status "Frontend logs: frontend.log"
    
    cd ..
}

# Stop servers
stop_servers() {
    print_status "Stopping servers..."
    
    # Stop backend
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_success "Backend server stopped"
        fi
        rm backend.pid
    fi
    
    # Stop frontend
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_success "Frontend server stopped"
        fi
        rm frontend.pid
    fi
    
    # Kill any remaining processes on ports 3000 and 8000
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
}

# Check server status
check_status() {
    print_status "Checking server status..."
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null; then
        print_success "Backend server is running"
    else
        print_warning "Backend server is not responding"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null; then
        print_success "Frontend server is running"
    else
        print_warning "Frontend server is not responding"
    fi
}

# Show usage information
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup      Set up the application (install dependencies)"
    echo "  start      Start both backend and frontend servers"
    echo "  stop       Stop all running servers"
    echo "  restart    Restart all servers"
    echo "  status     Check server status"
    echo "  train      Train ML models"
    echo "  logs       Show server logs"
    echo "  help       Show this help message"
    echo ""
    echo "Default (no command): setup and start"
}

# Show logs
show_logs() {
    echo "=== Backend Logs ==="
    if [ -f "backend.log" ]; then
        tail -n 50 backend.log
    else
        echo "No backend logs found"
    fi
    
    echo ""
    echo "=== Frontend Logs ==="
    if [ -f "frontend.log" ]; then
        tail -n 50 frontend.log
    else
        echo "No frontend logs found"
    fi
}

# Main script logic
case "${1:-start}" in
    setup)
        print_status "Setting up InvestShield..."
        check_python || exit 1
        check_node || exit 1
        setup_backend
        setup_frontend
        train_models
        print_success "Setup completed successfully!"
        ;;
    
    start)
        print_status "Starting InvestShield..."
        
        # Check if already set up
        if [ ! -d "backend/venv" ] || [ ! -d "frontend/node_modules" ]; then
            print_warning "Application not set up. Running setup first..."
            check_python || exit 1
            check_node || exit 1
            setup_backend
            setup_frontend
            train_models
        fi
        
        start_backend
        sleep 3  # Wait for backend to start
        start_frontend
        
        print_success "InvestShield is starting up!"
        print_status "Backend: http://localhost:8000"
        print_status "Frontend: http://localhost:3000"
        print_status "API Docs: http://localhost:8000/docs"
        print_status ""
        print_status "Waiting for servers to be ready..."
        
        # Wait for servers to be ready
        for i in {1..30}; do
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                print_success "Backend is ready!"
                break
            fi
            sleep 2
        done
        
        for i in {1..30}; do
            if curl -s http://localhost:3000 > /dev/null 2>&1; then
                print_success "Frontend is ready!"
                break
            fi
            sleep 2
        done
        
        echo ""
        echo "🎉 InvestShield is now running!"
        echo "📱 Open http://localhost:3000 in your browser"
        echo "📖 API documentation: http://localhost:8000/docs"
        echo ""
        echo "To stop the servers, run: $0 stop"
        ;;
    
    stop)
        stop_servers
        ;;
    
    restart)
        print_status "Restarting InvestShield..."
        stop_servers
        sleep 2
        start_backend
        sleep 3
        start_frontend
        print_success "InvestShield restarted!"
        ;;
    
    status)
        check_status
        ;;
    
    train)
        print_status "Training ML models..."
        train_models
        ;;
    
    logs)
        show_logs
        ;;
    
    help|--help|-h)
        show_usage
        ;;
    
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
