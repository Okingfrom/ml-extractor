#!/bin/bash

# ML Extractor - Development Setup Script
# This script sets up the development environment for the new React + FastAPI architecture

set -e

echo "🚀 Setting up ML Extractor Development Environment"
echo "=================================================="

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

# Check if we're in the right directory
if [ ! -f "README_NEW_ARCHITECTURE.md" ]; then
    print_error "Please run this script from the ML EXTRACTOR root directory"
    exit 1
fi

# Check prerequisites
print_status "Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16+ from https://nodejs.org/"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed. Please install Python 3.8+ from https://python.org/"
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm (usually comes with Node.js)"
    exit 1
fi

print_success "Prerequisites check passed"

# Setup Frontend
print_status "Setting up Frontend (React + Tailwind CSS)..."
cd frontend

if [ ! -f "package.json" ]; then
    print_error "Frontend package.json not found"
    exit 1
fi

print_status "Installing frontend dependencies..."
npm install

if [ $? -eq 0 ]; then
    print_success "Frontend dependencies installed successfully"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi

cd ..

# Setup Backend
print_status "Setting up Backend (FastAPI)..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
print_status "Installing backend dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "Backend dependencies installed successfully"
else
    print_error "Failed to install backend dependencies"
    exit 1
fi

cd ..

# Create environment file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    print_status "Creating environment configuration..."
    cat > backend/.env << EOF
# Application Configuration
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=true

# Database (SQLite for development)
DATABASE_URL=sqlite:///./ml_extractor.db

# File Storage
UPLOAD_DIR=uploads
MAX_FILE_SIZE=104857600

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Email (Optional - configure for production)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password

# AI Features (Optional)
# OPENAI_API_KEY=your-openai-api-key
# OPENAI_MODEL=gpt-3.5-turbo

# Redis (Optional)
# REDIS_URL=redis://localhost:6379
EOF
    print_success "Environment file created at backend/.env"
    print_warning "Please update the environment variables in backend/.env as needed"
fi

# Create uploads directory
mkdir -p uploads
mkdir -p backend/uploads

# Setup database
print_status "Setting up database..."
cd backend
source venv/bin/activate

python3 -c "
try:
    from database import create_tables
    create_tables()
    print('✅ Database tables created successfully')
except Exception as e:
    print(f'❌ Database setup failed: {e}')
    exit(1)
" 2>/dev/null

cd ..

# Create startup scripts
print_status "Creating startup scripts..."

# Frontend startup script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "🌐 Starting Frontend (React + Tailwind CSS)..."
cd frontend
npm start
EOF

# Backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Backend (FastAPI)..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF

# Development startup script (both services)
cat > start_dev.sh << 'EOF'
#!/bin/bash
echo "🔧 Starting Full Development Environment..."
echo "Frontend will be available at: http://localhost:3000"
echo "Backend API will be available at: http://localhost:8000"
echo "API Documentation will be available at: http://localhost:8000/docs"
echo ""

# Function to cleanup background processes
cleanup() {
    echo "Stopping services..."
    kill $(jobs -p) 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend in background
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
cd ../frontend
npm start &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
EOF

# Make scripts executable
chmod +x start_frontend.sh start_backend.sh start_dev.sh

print_success "Startup scripts created:"
print_status "  - start_frontend.sh (React app only)"
print_status "  - start_backend.sh (FastAPI only)"
print_status "  - start_dev.sh (Both frontend and backend)"

# Final setup verification
print_status "Running setup verification..."

# Check if we can import backend modules
cd backend
source venv/bin/activate
python3 -c "
import sys
sys.path.append('..')
try:
    from backend.main import app
    print('✅ Backend imports successfully')
except Exception as e:
    print(f'❌ Backend import failed: {e}')
" 2>/dev/null

cd ..

# Check if frontend builds
cd frontend
if npm run build > /dev/null 2>&1; then
    print_success "Frontend builds successfully"
    rm -rf build  # Clean up build directory
else
    print_warning "Frontend build test failed - check dependencies"
fi

cd ..

# Summary
echo ""
echo "🎉 Setup Complete!"
echo "=================="
print_success "ML Extractor development environment is ready!"
echo ""
echo "📋 Next Steps:"
echo "  1. Review and update backend/.env with your configuration"
echo "  2. Start the development environment:"
echo "     ${BLUE}./start_dev.sh${NC}"
echo ""
echo "🌐 Access Points:"
echo "  - Frontend (React): http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - Health Check: http://localhost:8000/health"
echo ""
echo "📚 Documentation:"
echo "  - New Architecture Guide: README_NEW_ARCHITECTURE.md"
echo "  - API Documentation: http://localhost:8000/docs (when running)"
echo ""
echo "🧪 Testing:"
echo "  - Frontend: cd frontend && npm test"
echo "  - Backend: cd backend && source venv/bin/activate && pytest"
echo ""
print_warning "Note: Make sure to configure environment variables in backend/.env before production use"

echo ""
echo "Happy coding! 🚀"
