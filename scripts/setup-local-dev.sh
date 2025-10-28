#!/bin/bash

# Local Development Setup Script for MemoryGraph
set -e

echo "🚀 Setting up MemoryGraph for local development..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    # Check for Podman
    if ! command -v podman &> /dev/null; then
        print_error "Podman is not installed. Please install Podman first."
        exit 1
    fi
    
    # Check for Podman Compose
    if ! command -v podman-compose &> /dev/null; then
        print_error "Podman Compose is not installed. Please install podman-compose first."
        echo "   You can install it with: pip install podman-compose"
        exit 1
    fi
    
    # Check for Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.12+ first."
        exit 1
    fi
    
    print_status "All requirements satisfied!"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating backend .env file..."
        cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://memorygraph:password@localhost:5432/memorygraph_dev
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_V1_STR=/api/v1
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
DEBUG=true
LOG_LEVEL=DEBUG
ENVIRONMENT=local

# AI API Keys (add your keys here)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
EOF
        print_warning "Please update backend/.env with your actual API keys and secret key!"
    fi
    
    cd ..
    print_status "Backend setup complete!"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating frontend .env file..."
        cat > .env << EOF
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=local
EOF
    fi
    
    cd ..
    print_status "Frontend setup complete!"
}

# Setup Podman services
setup_podman() {
    print_status "Setting up Podman services..."
    
    # Create podman-compose.override.yml for local development
    if [ ! -f "podman-compose.override.yml" ]; then
        print_status "Creating podman-compose.override.yml for local development..."
        cat > podman-compose.override.yml << EOF
version: '3.8'

services:
  postgres:
    environment:
      POSTGRES_DB: memorygraph_dev
      POSTGRES_USER: memorygraph
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://memorygraph:password@postgres:5432/memorygraph_dev
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=local
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_ENVIRONMENT=local
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm start

volumes:
  postgres_data:
  redis_data:
EOF
    fi
    
    print_status "Podman services setup complete!"
}

# Create development scripts
create_scripts() {
    print_status "Creating development scripts..."
    
    # Create start-dev.sh
    cat > start-dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting MemoryGraph development environment..."

# Start Podman services
podman-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Start backend in background
echo "🔧 Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend
echo "🎨 Starting frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ Development environment started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Database: localhost:5432"
echo "Redis: localhost:6379"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID; podman-compose down; exit" INT
wait
EOF

    chmod +x start-dev.sh
    
    # Create stop-dev.sh
    cat > stop-dev.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping MemoryGraph development environment..."

# Kill any running processes
pkill -f "uvicorn app.main:app"
pkill -f "npm start"

# Stop Podman services
podman-compose down

echo "✅ Development environment stopped!"
EOF

    chmod +x stop-dev.sh
    
    print_status "Development scripts created!"
}

# Main setup function
main() {
    print_status "Starting MemoryGraph local development setup..."
    
    check_requirements
    setup_backend
    setup_frontend
    setup_podman
    create_scripts
    
    print_status "🎉 Setup complete!"
    echo ""
    print_status "Next steps:"
    echo "1. Update backend/.env with your API keys and secret key"
    echo "2. Run './start-dev.sh' to start the development environment"
    echo "3. Visit http://localhost:3000 for the frontend"
    echo "4. Visit http://localhost:8000/docs for the API documentation"
    echo ""
    print_warning "Remember to keep your API keys secure and never commit them to version control!"
}

# Run main function
main "$@"