#!/bin/bash

# MemoryGraph Local Development Startup Script
# This script starts all services using Docker Compose

set -e

echo "🚀 Starting MemoryGraph Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "   Especially set your OPENAI_API_KEY if you want AI features."
    read -p "Press Enter to continue after editing .env file..."
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."

# Wait for PostgreSQL
echo "   Waiting for PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U memorygraph > /dev/null 2>&1; do
    sleep 2
done
echo "   ✅ PostgreSQL is ready"

# Wait for Redis
echo "   Waiting for Redis..."
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    sleep 2
done
echo "   ✅ Redis is ready"

# Wait for backend
echo "   Waiting for backend API..."
until curl -s http://localhost:8001/health > /dev/null 2>&1; do
    sleep 2
done
echo "   ✅ Backend API is ready"

# Wait for frontend
echo "   Waiting for frontend..."
until curl -s http://localhost:3001 > /dev/null 2>&1; do
    sleep 2
done
echo "   ✅ Frontend is ready"

echo ""
echo "🎉 MemoryGraph is now running!"
echo ""
echo "📱 Frontend: http://localhost:3001"
echo "🔧 Backend API: http://localhost:8001"
echo "📊 API Docs: http://localhost:8001/docs"
echo "🗄️  PostgreSQL: localhost:5433"
echo "🔴 Redis: localhost:6380"
echo ""
echo "To stop the services, run: ./stop.sh"
echo "To view logs, run: docker-compose logs -f"
echo ""

# Show running containers
echo "📋 Running containers:"
docker-compose ps
