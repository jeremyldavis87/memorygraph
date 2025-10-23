from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

from app.queries.graph_queries import GraphQueries

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MemoryGraph Graph Retriever Service",
    version="1.0.0",
    description="Retrieves contextual information from Neo4j knowledge graph"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph queries
graph_queries = GraphQueries()

class QueryRequest(BaseModel):
    query: str
    limit: int = 50
    user_id: Optional[int] = None

class RelatedEntitiesRequest(BaseModel):
    entity_name: str
    max_depth: int = 2
    limit: int = 50
    user_id: Optional[int] = None

class GraphContextRequest(BaseModel):
    note_id: Optional[int] = None
    entity_names: List[str] = []
    max_depth: int = 2
    limit: int = 50
    user_id: Optional[int] = None

class QueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    query_time: float
    result_count: int

class RelatedEntitiesResponse(BaseModel):
    entity: Dict[str, Any]
    related_entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    query_time: float

class GraphContextResponse(BaseModel):
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    context_summary: str
    query_time: float

@app.get("/")
async def root():
    return {"message": "MemoryGraph Graph Retriever Service", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    try:
        # Test Neo4j connection
        await graph_queries.test_connection()
        return {"status": "healthy", "service": "retriever", "neo4j": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "service": "retriever", "neo4j": "disconnected", "error": str(e)}

@app.post("/query", response_model=QueryResponse)
async def query_graph(request: QueryRequest):
    """
    Execute a custom Cypher query against the knowledge graph.
    """
    try:
        result = await graph_queries.execute_query(
            query=request.query,
            limit=request.limit,
            user_id=request.user_id
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

@app.post("/related-entities", response_model=RelatedEntitiesResponse)
async def get_related_entities(request: RelatedEntitiesRequest):
    """
    Get entities related to a specific entity within a certain depth.
    """
    try:
        result = await graph_queries.get_related_entities(
            entity_name=request.entity_name,
            max_depth=request.max_depth,
            limit=request.limit,
            user_id=request.user_id
        )
        return RelatedEntitiesResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Related entities query failed: {str(e)}")

@app.post("/graph-context", response_model=GraphContextResponse)
async def get_graph_context(request: GraphContextRequest):
    """
    Get contextual information for a note or set of entities.
    """
    try:
        result = await graph_queries.get_graph_context(
            note_id=request.note_id,
            entity_names=request.entity_names,
            max_depth=request.max_depth,
            limit=request.limit,
            user_id=request.user_id
        )
        return GraphContextResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph context query failed: {str(e)}")

@app.get("/entity/{entity_name}")
async def get_entity_details(entity_name: str):
    """
    Get detailed information about a specific entity.
    """
    try:
        result = await graph_queries.get_entity_details(entity_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Entity not found: {str(e)}")

@app.get("/search/{search_term}")
async def search_entities(search_term: str, limit: int = 20):
    """
    Search for entities by name or properties.
    """
    try:
        result = await graph_queries.search_entities(search_term, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/stats")
async def get_graph_stats():
    """
    Get statistics about the knowledge graph.
    """
    try:
        stats = await graph_queries.get_graph_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@app.get("/recommendations/{entity_name}")
async def get_recommendations(entity_name: str, limit: int = 10):
    """
    Get recommendations based on graph structure and relationships.
    """
    try:
        result = await graph_queries.get_recommendations(entity_name, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
