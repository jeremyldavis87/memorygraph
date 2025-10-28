#!/bin/bash

# MemoryGraph Local Development Stop Script
# This script stops all services and cleans up

set -e

echo "🛑 Stopping MemoryGraph Development Environment..."

# Check if Podman Compose is available
if ! command -v podman-compose &> /dev/null; then
    echo "❌ Podman Compose is not installed."
    exit 1
fi

# Stop and remove containers
echo "🐳 Stopping Podman containers..."
podman-compose -f podman-compose.yml down

# Optional: Remove volumes (uncomment if you want to reset the database)
# echo "🗑️  Removing volumes..."
# podman-compose -f podman-compose.yml down -v

# Optional: Remove images (uncomment if you want to clean up images)
# echo "🧹 Removing images..."
# podman-compose -f podman-compose.yml down --rmi all

echo "✅ MemoryGraph has been stopped!"
echo ""
echo "To start again, run: ./start.sh"
echo "To view logs from the last run, run: podman-compose -f podman-compose.yml logs"
