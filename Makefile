# MemoryGraph Development Makefile

.PHONY: help setup dev test clean build deploy-dev deploy-prod

# Default target
help:
	@echo "MemoryGraph Development Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  setup          - Run initial setup for local development"
	@echo "  install        - Install all dependencies"
	@echo ""
	@echo "Development:"
	@echo "  dev            - Start development environment"
	@echo "  dev-services   - Start only Docker services (DB, Redis)"
	@echo "  stop           - Stop all development services"
	@echo "  clean          - Clean up containers and volumes"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-backend   - Run backend tests"
	@echo "  test-frontend  - Run frontend tests"
	@echo "  test-build     - Test frontend build"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy-dev     - Deploy to dev environment"
	@echo "  deploy-prod    - Deploy to prod environment"
	@echo ""

# Setup
setup:
	@echo "🚀 Setting up MemoryGraph for local development..."
	@./scripts/setup-local-dev.sh

install:
	@echo "📦 Installing dependencies..."
	@cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@cd frontend && npm install

# Development
dev:
	@echo "🚀 Starting development environment..."
	@./start-dev.sh

dev-services:
	@echo "🐳 Starting Docker services..."
	@docker-compose -f docker-compose.local.yml up -d
	@echo "✅ Services started! Backend and frontend need to be started separately."

stop:
	@echo "🛑 Stopping development environment..."
	@./stop-dev.sh

clean:
	@echo "🧹 Cleaning up containers and volumes..."
	@docker-compose -f docker-compose.local.yml down -v
	@docker system prune -f

# Testing
test: test-backend test-frontend test-build

test-backend:
	@echo "🧪 Running backend tests..."
	@cd backend && source venv/bin/activate && python -m pytest tests/ -v

test-frontend:
	@echo "🧪 Running frontend tests..."
	@cd frontend && npm test -- --coverage --watchAll=false --passWithNoTests

test-build:
	@echo "🏗️ Testing frontend build..."
	@cd frontend && npm run build

# Deployment (these would typically be run by CI/CD)
deploy-dev:
	@echo "🚀 Deploying to dev environment..."
	@echo "This should be triggered by pushing to the develop branch"

deploy-prod:
	@echo "🚀 Deploying to prod environment..."
	@echo "This should be triggered by pushing to the main branch"