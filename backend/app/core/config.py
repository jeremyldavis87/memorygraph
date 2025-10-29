from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Union
from pydantic import Field
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env.development first, before Settings is initialized
env_path = Path(__file__).parent.parent / ".env.development"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment from: {env_path}")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.development",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    PROJECT_NAME: str = "MemoryGraph"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://memorygraph:password@localhost:5432/memorygraph")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # AI/ML
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    BRAINTRUST_API_KEY: Optional[str] = os.getenv("BRAINTRUST_API_KEY")
    OCR_MODE: str = os.getenv("OCR_MODE", "llm")  # traditional, llm, or auto - default to LLM for better results
    
    # Agent Configuration
    AGENT_VISION_MODEL: str = os.getenv("AGENT_VISION_MODEL", "gpt-4o-mini")
    AGENT_OCR_CONFIDENCE_THRESHOLD: int = int(os.getenv("AGENT_OCR_CONFIDENCE_THRESHOLD", "90"))
    AGENT_PROCESSING_TIMEOUT: int = int(os.getenv("AGENT_PROCESSING_TIMEOUT", "30"))  # seconds
    AGENT_PARALLEL_PROCESSING_LIMIT: int = int(os.getenv("AGENT_PARALLEL_PROCESSING_LIMIT", "5"))
    AGENT_MAX_RETRIES: int = int(os.getenv("AGENT_MAX_RETRIES", "1"))
    AGENT_ENABLE_BRAINTRUST: bool = os.getenv("AGENT_ENABLE_BRAINTRUST", "true").lower() == "true"
    
    # Color-to-Category Mappings (not parsed from env - use default)
    AGENT_COLOR_CATEGORY_MAPPINGS: dict = Field(
        default={
            "yellow": "general",
            "pink": "urgent", 
            "blue": "work",
            "green": "personal",
            "orange": "ideas",
            "white": "notes",
            "gray": "archive"
        },
        exclude=True  # Don't parse from env file
    )
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse BACKEND_CORS_ORIGINS if it's a JSON string
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            try:
                self.BACKEND_CORS_ORIGINS = json.loads(self.BACKEND_CORS_ORIGINS)
            except json.JSONDecodeError:
                # If it's not JSON, split by comma
                self.BACKEND_CORS_ORIGINS = [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(',')]
    
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
    
settings = Settings()