import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio
import os
from app.core.config import settings

class Triple(BaseModel):
    subject: str
    predicate: str
    object: str
    confidence: float
    entity_type: str
    relationship_type: str
    properties: Dict[str, Any] = {}

class ExtractRequest(BaseModel):
    content: str
    title: Optional[str] = None
    source_type: str = "rocketbook"
    user_id: Optional[int] = None

class ExtractResponse(BaseModel):
    triples: List[Triple]
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    processing_time: float
    model_used: str

class InsertRequest(BaseModel):
    triples: List[Triple]
    note_id: Optional[int] = None
    user_id: Optional[int] = None

class InsertResponse(BaseModel):
    inserted_count: int
    merged_count: int
    errors: List[str] = []
    processing_time: float

class GraphContextRequest(BaseModel):
    note_id: Optional[int] = None
    entity_names: List[str] = []
    max_depth: int = 2
    limit: int = 50
    user_id: Optional[int] = None

class GraphContextResponse(BaseModel):
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    context_summary: str
    query_time: float

class GraphServiceClient:
    def __init__(self):
        self.extractor_url = settings.EXTRACTOR_SERVICE_URL
        self.inserter_url = settings.INSERTER_SERVICE_URL
        self.retriever_url = settings.RETRIEVER_SERVICE_URL
        
        # HTTP client with timeout
        self.client = httpx.AsyncClient(timeout=30.0)

    async def extract_triples(self, content: str, title: Optional[str] = None, 
                           source_type: str = "rocketbook", user_id: Optional[int] = None) -> ExtractResponse:
        """
        Extract knowledge graph triples from note content.
        """
        try:
            response = await self.client.post(
                f"{self.extractor_url}/extract",
                json={
                    "content": content,
                    "title": title,
                    "source_type": source_type,
                    "user_id": user_id
                }
            )
            response.raise_for_status()
            return ExtractResponse(**response.json())
        except httpx.HTTPError as e:
            raise Exception(f"Extraction service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Triple extraction failed: {str(e)}")

    async def extract_triples_async(self, note_id: int, content: str, title: Optional[str] = None,
                                 source_type: str = "rocketbook", user_id: int = None) -> str:
        """
        Queue an async triple extraction job.
        """
        try:
            response = await self.client.post(
                f"{self.extractor_url}/extract/async",
                json={
                    "note_id": note_id,
                    "content": content,
                    "title": title,
                    "source_type": source_type,
                    "user_id": user_id
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["job_id"]
        except httpx.HTTPError as e:
            raise Exception(f"Async extraction service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Async triple extraction failed: {str(e)}")

    async def get_extraction_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of an extraction job.
        """
        try:
            response = await self.client.get(f"{self.extractor_url}/extract/status/{job_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Status check service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Status check failed: {str(e)}")

    async def get_extraction_result(self, job_id: str) -> ExtractResponse:
        """
        Get the result of a completed extraction job.
        """
        try:
            response = await self.client.get(f"{self.extractor_url}/extract/result/{job_id}")
            response.raise_for_status()
            return ExtractResponse(**response.json())
        except httpx.HTTPError as e:
            raise Exception(f"Result retrieval service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Result retrieval failed: {str(e)}")

    async def insert_triples(self, triples: List[Triple], note_id: Optional[int] = None, 
                           user_id: Optional[int] = None) -> InsertResponse:
        """
        Insert knowledge graph triples into Neo4j.
        """
        try:
            response = await self.client.post(
                f"{self.inserter_url}/insert",
                json={
                    "triples": [triple.dict() for triple in triples],
                    "note_id": note_id,
                    "user_id": user_id
                }
            )
            response.raise_for_status()
            return InsertResponse(**response.json())
        except httpx.HTTPError as e:
            raise Exception(f"Insertion service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Triple insertion failed: {str(e)}")

    async def bulk_insert_triples(self, triples: List[Triple], note_id: Optional[int] = None,
                                user_id: Optional[int] = None, batch_size: int = 100) -> InsertResponse:
        """
        Insert knowledge graph triples in batches for better performance.
        """
        try:
            response = await self.client.post(
                f"{self.inserter_url}/bulk-insert",
                json={
                    "triples": [triple.dict() for triple in triples],
                    "note_id": note_id,
                    "user_id": user_id,
                    "batch_size": batch_size
                }
            )
            response.raise_for_status()
            return InsertResponse(**response.json())
        except httpx.HTTPError as e:
            raise Exception(f"Bulk insertion service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Bulk triple insertion failed: {str(e)}")

    async def get_graph_context(self, note_id: Optional[int] = None, 
                              entity_names: List[str] = [], max_depth: int = 2,
                              limit: int = 50, user_id: Optional[int] = None) -> GraphContextResponse:
        """
        Get contextual information for a note or set of entities.
        """
        try:
            response = await self.client.post(
                f"{self.retriever_url}/graph-context",
                json={
                    "note_id": note_id,
                    "entity_names": entity_names,
                    "max_depth": max_depth,
                    "limit": limit,
                    "user_id": user_id
                }
            )
            response.raise_for_status()
            return GraphContextResponse(**response.json())
        except httpx.HTTPError as e:
            raise Exception(f"Context retrieval service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Graph context retrieval failed: {str(e)}")

    async def get_related_entities(self, entity_name: str, max_depth: int = 2,
                                 limit: int = 50, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get entities related to a specific entity.
        """
        try:
            response = await self.client.post(
                f"{self.retriever_url}/related-entities",
                json={
                    "entity_name": entity_name,
                    "max_depth": max_depth,
                    "limit": limit,
                    "user_id": user_id
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Related entities service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Related entities retrieval failed: {str(e)}")

    async def search_entities(self, search_term: str, limit: int = 20) -> Dict[str, Any]:
        """
        Search for entities by name or properties.
        """
        try:
            response = await self.client.get(
                f"{self.retriever_url}/search/{search_term}",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Entity search service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Entity search failed: {str(e)}")

    async def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.
        """
        try:
            response = await self.client.get(f"{self.retriever_url}/stats")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Stats service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Graph stats retrieval failed: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of all graph services.
        """
        health_status = {
            "extractor": {"status": "unknown", "error": None},
            "inserter": {"status": "unknown", "error": None},
            "retriever": {"status": "unknown", "error": None}
        }
        
        # Check extractor service
        try:
            response = await self.client.get(f"{self.extractor_url}/health")
            health_status["extractor"] = response.json()
        except Exception as e:
            health_status["extractor"] = {"status": "unhealthy", "error": str(e)}
        
        # Check inserter service
        try:
            response = await self.client.get(f"{self.inserter_url}/health")
            health_status["inserter"] = response.json()
        except Exception as e:
            health_status["inserter"] = {"status": "unhealthy", "error": str(e)}
        
        # Check retriever service
        try:
            response = await self.client.get(f"{self.retriever_url}/health")
            health_status["retriever"] = response.json()
        except Exception as e:
            health_status["retriever"] = {"status": "unhealthy", "error": str(e)}
        
        return health_status

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Global instance
graph_client = GraphServiceClient()
