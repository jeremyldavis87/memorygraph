from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "MemoryGraph"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://memorygraph:password@localhost:5432/memorygraph")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # AI/ML
    OPENAI_API_KEY: Optional[str] = None
    BRAINTRUST_API_KEY: Optional[str] = None
    OCR_MODE: str = "traditional"  # traditional, llm, or auto
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Development
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Neo4j Configuration
    NEO4J_URI: str = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")
    AURA_INSTANCEID: Optional[str] = os.getenv("AURA_INSTANCEID")
    AURA_INSTANCENAME: Optional[str] = os.getenv("AURA_INSTANCENAME")
    
    # Graph Services Configuration
    GRAPH_EXTRACTION_LLM_PROVIDER: str = os.getenv("GRAPH_EXTRACTION_LLM_PROVIDER", "openai")
    GRAPH_EXTRACTION_MODEL: str = os.getenv("GRAPH_EXTRACTION_MODEL", "gpt-5-mini")
    EXTRACTOR_SERVICE_URL: str = os.getenv("EXTRACTOR_SERVICE_URL", "http://localhost:8002")
    INSERTER_SERVICE_URL: str = os.getenv("INSERTER_SERVICE_URL", "http://localhost:8003")
    RETRIEVER_SERVICE_URL: str = os.getenv("RETRIEVER_SERVICE_URL", "http://localhost:8004")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()