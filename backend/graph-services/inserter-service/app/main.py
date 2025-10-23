from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

from app.db.neo4j_client import Neo4jClient

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MemoryGraph Graph Inserter Service",
    version="1.0.0",
    description="Inserts knowledge graph triples into Neo4j database"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Neo4j client
neo4j_client = Neo4jClient()

class Triple(BaseModel):
    subject: str
    predicate: str
    object: str
    confidence: float
    entity_type: str
    relationship_type: str
    properties: Dict[str, Any] = {}

class InsertRequest(BaseModel):
    triples: List[Triple]
    note_id: Optional[int] = None
    user_id: Optional[int] = None

class BulkInsertRequest(BaseModel):
    triples: List[Triple]
    note_id: Optional[int] = None
    user_id: Optional[int] = None
    batch_size: int = 100

class MergeEntityRequest(BaseModel):
    entity_name: str
    entity_type: str
    properties: Dict[str, Any] = {}
    merge_strategy: str = "merge"  # merge, create, update

class InsertResponse(BaseModel):
    inserted_count: int
    merged_count: int
    errors: List[str] = []
    processing_time: float

class MergeResponse(BaseModel):
    entity_id: str
    action: str  # created, merged, updated
    properties: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "MemoryGraph Graph Inserter Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    try:
        # Test Neo4j connection
        await neo4j_client.test_connection()
        return {"status": "healthy", "service": "inserter", "neo4j": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "service": "inserter", "neo4j": "disconnected", "error": str(e)}

@app.post("/insert", response_model=InsertResponse)
async def insert_triples(request: InsertRequest):
    """
    Insert knowledge graph triples into Neo4j.
    """
    try:
        result = await neo4j_client.insert_triples(
            triples=request.triples,
            note_id=request.note_id,
            user_id=request.user_id
        )
        return InsertResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insertion failed: {str(e)}")

@app.post("/bulk-insert", response_model=InsertResponse)
async def bulk_insert_triples(request: BulkInsertRequest):
    """
    Insert knowledge graph triples in batches for better performance.
    """
    try:
        result = await neo4j_client.bulk_insert_triples(
            triples=request.triples,
            note_id=request.note_id,
            user_id=request.user_id,
            batch_size=request.batch_size
        )
        return InsertResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk insertion failed: {str(e)}")

@app.post("/merge-entity", response_model=MergeResponse)
async def merge_entity(request: MergeEntityRequest):
    """
    Merge or create an entity in the knowledge graph.
    """
    try:
        result = await neo4j_client.merge_entity(
            name=request.entity_name,
            entity_type=request.entity_type,
            properties=request.properties,
            strategy=request.merge_strategy
        )
        return MergeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity merge failed: {str(e)}")

@app.get("/entity/{entity_name}")
async def get_entity(entity_name: str):
    """
    Get an entity and its relationships from the knowledge graph.
    """
    try:
        result = await neo4j_client.get_entity(entity_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Entity not found: {str(e)}")

@app.delete("/entity/{entity_name}")
async def delete_entity(entity_name: str):
    """
    Delete an entity and its relationships from the knowledge graph.
    """
    try:
        result = await neo4j_client.delete_entity(entity_name)
        return {"message": f"Entity '{entity_name}' deleted", "relationships_deleted": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity deletion failed: {str(e)}")

@app.get("/stats")
async def get_graph_stats():
    """
    Get statistics about the knowledge graph.
    """
    try:
        stats = await neo4j_client.get_graph_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
