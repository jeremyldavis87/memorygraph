# MemoryGraph - AI-Powered Knowledge Management Platform

MemoryGraph is an AI-native knowledge management and personal assistant platform that captures information from any source, understands context through advanced AI processing, and maintains a knowledge graph of relationships and entities.

## 🚀 Features

### Phase 1: Rocketbook Capture Core (Current)
- **Smart Note Capture**: Camera interface optimized for Rocketbook sticky notes
- **QR Code Detection**: Automatic categorization based on QR codes
- **Dual-Mode OCR**: Traditional (fast/offline) and LLM (accurate/online) processing
- **AI Context Agent**: Automatic entity extraction, summaries, and action items
- **Knowledge Graph**: Visual representation of relationships between concepts
- **Natural Language Search**: Find information using conversational queries
- **Multi-Device Sync**: Access your knowledge base from anywhere

### Future Phases
- **Multi-Modal Capture**: Audio, video, documents, web content
- **AI Assistant**: Proactive information surfacing and insights
- **Team Collaboration**: Shared knowledge graphs and workspaces
- **Advanced Intelligence**: Pattern detection and hypothesis generation

## 🏗️ Project Structure

```
memorygraph/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── tests/              # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── contexts/       # React contexts
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   ├── package.json
│   └── Dockerfile
├── infrastructure/         # Terraform configuration
├── .github/workflows/      # CI/CD pipelines
├── docker-compose.yml      # Development environment
└── .env.example           # Environment variables template
```

## 🛠️ Technology Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **AI/ML**: OpenAI API, Tesseract OCR, OpenCV
- **Database**: PostgreSQL with graph extensions
- **Infrastructure**: Docker, Terraform, AWS ECS
- **CI/CD**: GitHub Actions
- **Authentication**: JWT tokens with bcrypt

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.12+ (for local development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd memorygraph
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the development environment**
   ```bash
   docker-compose up
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 📱 Usage

### Getting Started
1. **Register** for a new account or **login** with existing credentials
2. **Configure Categories** by mapping QR codes to your organizational system
3. **Capture Notes** using the camera interface or file upload
4. **Search** your knowledge base using natural language queries
5. **Explore** the knowledge graph to discover connections

### Key Features

#### Smart Note Capture
- Position your Rocketbook note in the camera view
- QR code detection automatically categorizes your note
- Choose between fast (traditional) or accurate (AI) OCR processing
- Review and edit extracted text before saving

#### AI-Powered Processing
- Automatic entity extraction (people, projects, concepts)
- Smart summaries and insights
- Action item detection and tracking
- Related note suggestions

#### Knowledge Graph
- Visual representation of relationships between entities
- Click on any entity to see all related notes
- Discover unexpected connections across your knowledge

#### Natural Language Search
- Search using conversational queries
- "Show me notes about project X from last month"
- "Find all action items assigned to John"
- "What did I discuss in the meeting about AI?"

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 Deployment

### Using Docker Compose (Production)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Using Terraform (AWS)
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

### Environment Variables
See `.env.example` for required environment variables:
- Database configuration
- OpenAI API key for AI processing
- JWT secret key
- CORS settings

## 📊 API Documentation

The API is fully documented with OpenAPI/Swagger:
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/notes/` - List notes with search/filter
- `POST /api/v1/notes/upload` - Upload and process note
- `GET /api/v1/search/notes` - Natural language search
- `GET /api/v1/entities/` - List knowledge graph entities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions

## 🗺️ Roadmap

### Phase 1 (Current) - Rocketbook Capture Core
- [x] Basic note capture and OCR
- [x] QR code detection and categorization
- [x] AI-powered entity extraction
- [x] Knowledge graph visualization
- [x] Natural language search
- [ ] Advanced OCR with LLM integration
- [ ] Mobile app optimization

### Phase 2 - Multi-Modal Capture
- [ ] Audio recording and transcription
- [ ] Video capture and processing
- [ ] Document scanning and processing
- [ ] Web content capture
- [ ] Email integration

### Phase 3 - AI Assistant & Integrations
- [ ] Proactive information surfacing
- [ ] Calendar and task management integration
- [ ] Team collaboration features
- [ ] Content generation from knowledge base

### Phase 4 - Advanced Intelligence
- [ ] Pattern detection and trend analysis
- [ ] Hypothesis generation
- [ ] Research assistant mode
- [ ] Plugin architecture

---

**Built with ❤️ for knowledge workers who want to remember everything, connect everything, and understand everything.**