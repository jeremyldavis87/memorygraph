from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

from app.extractors.triple_extractor import TripleExtractor

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MemoryGraph Triple Extractor Service",
    version="1.0.0",
    description="Extracts knowledge graph triples from note content using LLM"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize triple extractor
extractor = TripleExtractor()

class ExtractRequest(BaseModel):
    note_id: Optional[int] = None
    content: str
    title: Optional[str] = None
    source_type: str = "rocketbook"
    user_id: Optional[int] = None

class Triple(BaseModel):
    subject: str
    predicate: str
    object: str
    confidence: float
    entity_type: str
    relationship_type: str

class ExtractResponse(BaseModel):
    triples: List[Triple]
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    processing_time: float
    model_used: str

class AsyncExtractRequest(BaseModel):
    note_id: int
    content: str
    title: Optional[str] = None
    source_type: str = "rocketbook"
    user_id: int

class AsyncExtractResponse(BaseModel):
    job_id: str
    status: str
    message: str

@app.get("/")
async def root():
    return {"message": "MemoryGraph Triple Extractor Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "extractor"}

@app.post("/extract", response_model=ExtractResponse)
async def extract_triples(request: ExtractRequest):
    """
    Extract knowledge graph triples from note content synchronously.
    """
    try:
        result = await extractor.extract_triples(
            content=request.content,
            title=request.title,
            source_type=request.source_type,
            user_id=request.user_id
        )
        return ExtractResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@app.post("/extract/async", response_model=AsyncExtractResponse)
async def extract_triples_async(request: AsyncExtractRequest):
    """
    Extract knowledge graph triples from note content asynchronously.
    Returns a job ID for tracking the extraction process.
    """
    try:
        job_id = await extractor.extract_triples_async(
            note_id=request.note_id,
            content=request.content,
            title=request.title,
            source_type=request.source_type,
            user_id=request.user_id
        )
        return AsyncExtractResponse(
            job_id=job_id,
            status="queued",
            message="Extraction job queued successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Async extraction failed: {str(e)}")

@app.get("/extract/status/{job_id}")
async def get_extraction_status(job_id: str):
    """
    Get the status of an async extraction job.
    """
    try:
        status = await extractor.get_extraction_status(job_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")

@app.get("/extract/result/{job_id}")
async def get_extraction_result(job_id: str):
    """
    Get the result of a completed extraction job.
    """
    try:
        result = await extractor.get_extraction_result(job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Result not found: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
