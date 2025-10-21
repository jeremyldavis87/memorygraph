# MemoryGraph - AI-Powered Knowledge Management Platform

MemoryGraph is an AI-native knowledge management and personal assistant platform that captures information from any source, understands context through advanced AI processing, and maintains a knowledge graph of relationships and entities.

## Project Structure

```
memorygraph/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── package.json
│   └── Dockerfile
├── infrastructure/         # Terraform configuration
├── docker-compose.yml      # Development environment
└── .env.example           # Environment variables template
```

## Phase 1: Rocketbook Capture Core

This initial phase focuses on:
- Camera interface for scanning Rocketbook notes
- QR code detection and categorization
- Dual-mode OCR (traditional + LLM)
- Knowledge graph construction
- Natural language search
- Multi-device sync

## Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run `docker-compose up` for development environment
4. Access frontend at http://localhost:3000
5. Access backend API at http://localhost:8000

## Technology Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, TypeScript, Tailwind CSS
- **AI/ML**: OpenAI API, Tesseract OCR
- **Database**: PostgreSQL with graph extensions
- **Infrastructure**: Docker, Terraform
- **CI/CD**: GitHub Actions