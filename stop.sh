#!/bin/bash

# MemoryGraph Local Development Stop Script
# This script stops all services and cleans up

set -e

echo "🛑 Stopping MemoryGraph Development Environment..."

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

# Stop and remove containers
echo "🐳 Stopping Docker containers..."
docker-compose down

# Optional: Remove volumes (uncomment if you want to reset the database)
# echo "🗑️  Removing volumes..."
# docker-compose down -v

# Optional: Remove images (uncomment if you want to clean up images)
# echo "🧹 Removing images..."
# docker-compose down --rmi all

echo "✅ MemoryGraph has been stopped!"
echo ""
echo "To start again, run: ./start.sh"
echo "To view logs from the last run, run: docker-compose logs"
