from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.database import engine, Base
from app.core.logging_config import setup_logging, log_request, log_info

# Set up logging
setup_logging(log_level=settings.LOG_LEVEL)
log_info("Starting MemoryGraph API", version=settings.VERSION)

# Create database tables only if not in test environment
if not os.getenv("TESTING"):
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered knowledge management platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add request logging middleware
app.middleware("http")(log_request)

# Set up CORS
log_info("CORS Origins configured", origins=settings.BACKEND_CORS_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    log_info("Root endpoint accessed")
    return {"message": "MemoryGraph API", "version": settings.VERSION}

@app.get("/health")
async def health_check():
    log_info("Health check endpoint accessed")
    return {"status": "healthy"}