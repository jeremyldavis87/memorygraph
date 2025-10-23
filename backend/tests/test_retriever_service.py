import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add the graph services to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'graph-services', 'retriever-service'))

from app.main import app as retriever_app
from app.queries.graph_queries import GraphQueries

retriever_client = TestClient(retriever_app)

@pytest.fixture
def mock_neo4j():
    """Mock Neo4j driver for testing"""
    with patch('app.queries.graph_queries.AsyncGraphDatabase.driver') as mock_driver:
        mock_session = AsyncMock()
        mock_driver.return_value.session.return_value.__aenter__.return_value = mock_session
        yield mock_session

def test_retriever_health_check(mock_neo4j):
    """Test retriever service health endpoint"""
    # Mock successful connection test
    mock_neo4j.run.return_value.single.return_value = {"test": 1}
    
    response = retriever_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "retriever"
    assert data["neo4j"] == "connected"

def test_retriever_health_check_failure():
    """Test retriever service health endpoint when Neo4j is down"""
    with patch('app.queries.graph_queries.AsyncGraphDatabase.driver') as mock_driver:
        mock_driver.side_effect = Exception("Connection failed")
        
        response = retriever_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["neo4j"] == "disconnected"

def test_query_graph(mock_neo4j):
    """Test executing custom Cypher query"""
    # Mock query results
    mock_neo4j.run.return_value.data.return_value = [
        {"name": "John Smith", "type": "Person"},
        {"name": "Acme Corp", "type": "Organization"}
    ]
    
    response = retriever_client.post("/query", json={
        "query": "MATCH (n) RETURN n.name as name, n.type as type LIMIT 10",
        "limit": 10,
        "user_id": 1
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "query_time" in data
    assert "result_count" in data
    assert len(data["results"]) == 2

def test_get_related_entities(mock_neo4j):
    """Test getting related entities"""
    # Mock related entities query
    mock_neo4j.run.return_value.single.return_value = {
        "entity": {"name": "John Smith", "type": "Person"},
        "related_entities": [
            {
                "entity": {"name": "Acme Corp", "type": "Organization"},
                "path": [{"type": "WORKS_FOR", "properties": {}}],
                "distance": 1
            }
        ]
    }
    
    response = retriever_client.post("/related-entities", json={
        "entity_name": "John Smith",
        "max_depth": 2,
        "limit": 50,
        "user_id": 1
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "entity" in data
    assert "related_entities" in data
    assert "relationships" in data
    assert "query_time" in data
    assert data["entity"]["name"] == "John Smith"

def test_get_graph_context_by_note_id(mock_neo4j):
    """Test getting graph context for a note"""
    # Mock context query
    mock_neo4j.run.return_value.single.return_value = {
        "entities": [
            {"name": "John Smith", "type": "Person"},
            {"name": "Acme Corp", "type": "Organization"}
        ],
        "relationships": [
            {"from": "John Smith", "to": "Acme Corp", "type": "WORKS_FOR", "properties": {}}
        ]
    }
    
    response = retriever_client.post("/graph-context", json={
        "note_id": 1,
        "max_depth": 2,
        "limit": 50,
        "user_id": 1
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert "relationships" in data
    assert "context_summary" in data
    assert "query_time" in data
    assert len(data["entities"]) == 2

def test_get_graph_context_by_entity_names(mock_neo4j):
    """Test getting graph context for specific entities"""
    # Mock context query
    mock_neo4j.run.return_value.single.return_value = {
        "entities": [
            {"name": "John Smith", "type": "Person"},
            {"name": "Acme Corp", "type": "Organization"}
        ],
        "relationships": [
            {"from": "John Smith", "to": "Acme Corp", "type": "WORKS_FOR", "properties": {}}
        ]
    }
    
    response = retriever_client.post("/graph-context", json={
        "entity_names": ["John Smith", "Acme Corp"],
        "max_depth": 2,
        "limit": 50,
        "user_id": 1
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert "relationships" in data
    assert "context_summary" in data
    assert "query_time" in data

def test_get_entity_details(mock_neo4j):
    """Test getting entity details"""
    # Mock entity details query
    mock_neo4j.run.return_value.single.return_value = {
        "entity": {"name": "John Smith", "type": "Person"},
        "relationships": [
            {
                "relationship": "WORKS_FOR",
                "direction": "outgoing",
                "target": "Acme Corp",
                "properties": {}
            }
        ],
        "relationship_count": 1
    }
    
    response = retriever_client.get("/entity/John Smith")
    
    assert response.status_code == 200
    data = response.json()
    assert "entity" in data
    assert "relationships" in data
    assert "relationship_count" in data
    assert data["entity"]["name"] == "John Smith"

def test_get_entity_details_not_found(mock_neo4j):
    """Test getting non-existent entity details"""
    # Mock entity not found
    mock_neo4j.run.return_value.single.return_value = None
    
    response = retriever_client.get("/entity/NonExistent")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]

def test_search_entities(mock_neo4j):
    """Test searching entities"""
    # Mock search results
    mock_neo4j.run.return_value.data.return_value = [
        {"entity": {"name": "John Smith", "type": "Person"}, "relevance_score": 1.0},
        {"entity": {"name": "John Doe", "type": "Person"}, "relevance_score": 0.8}
    ]
    
    response = retriever_client.get("/search/John?limit=20")
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert len(data["results"]) == 2

def test_get_graph_stats(mock_neo4j):
    """Test getting graph statistics"""
    # Mock stats queries
    mock_neo4j.run.return_value.single.side_effect = [
        {"total_nodes": 10, "entity_count": 8, "note_count": 2},
        {"total_relationships": 5, "relationship_types": 3}
    ]
    mock_neo4j.run.return_value.data.return_value = [
        {"entity_type": "Person", "count": 5},
        {"entity_type": "Organization", "count": 3}
    ]
    
    response = retriever_client.get("/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_nodes" in data
    assert "entity_count" in data
    assert "note_count" in data
    assert "total_relationships" in data
    assert "relationship_types" in data
    assert "entity_type_distribution" in data

def test_get_recommendations(mock_neo4j):
    """Test getting entity recommendations"""
    # Mock recommendations query
    mock_neo4j.run.return_value.data.return_value = [
        {
            "entity": {"name": "Sarah Johnson", "type": "Person"},
            "common_connections": 2,
            "relationship_types": ["WORKS_FOR"],
            "recommendation_score": 0.8
        }
    ]
    
    response = retriever_client.get("/recommendations/John Smith?limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "count" in data
    assert len(data["recommendations"]) == 1

def test_graph_queries_initialization():
    """Test GraphQueries initialization"""
    with patch.dict(os.environ, {
        'NEO4J_URI': 'neo4j://localhost:7687',
        'NEO4J_USERNAME': 'neo4j',
        'NEO4J_PASSWORD': 'password',
        'NEO4J_DATABASE': 'neo4j'
    }):
        queries = GraphQueries()
        assert queries.uri == 'neo4j://localhost:7687'
        assert queries.username == 'neo4j'
        assert queries.password == 'password'
        assert queries.database == 'neo4j'

def test_graph_queries_test_connection(mock_neo4j):
    """Test GraphQueries connection test"""
    mock_neo4j.run.return_value.single.return_value = {"test": 1}
    
    queries = GraphQueries()
    result = asyncio.run(queries.test_connection())
    assert result is True

def test_graph_queries_test_connection_failure():
    """Test GraphQueries connection test failure"""
    with patch('app.queries.graph_queries.AsyncGraphDatabase.driver') as mock_driver:
        mock_driver.side_effect = Exception("Connection failed")
        
        queries = GraphQueries()
        with pytest.raises(Exception, match="Neo4j connection failed"):
            asyncio.run(queries.test_connection())

def test_graph_queries_execute_query(mock_neo4j):
    """Test executing query through GraphQueries"""
    mock_neo4j.run.return_value.data.return_value = [
        {"name": "John Smith", "type": "Person"}
    ]
    
    queries = GraphQueries()
    result = asyncio.run(queries.execute_query("MATCH (n) RETURN n", limit=10))
    
    assert "results" in result
    assert "query_time" in result
    assert "result_count" in result
    assert len(result["results"]) == 1

def test_graph_queries_get_related_entities(mock_neo4j):
    """Test getting related entities through GraphQueries"""
    mock_neo4j.run.return_value.single.return_value = {
        "entity": {"name": "John Smith", "type": "Person"},
        "related_entities": []
    }
    
    queries = GraphQueries()
    result = asyncio.run(queries.get_related_entities("John Smith", max_depth=2))
    
    assert "entity" in result
    assert "related_entities" in result
    assert "relationships" in result
    assert "query_time" in result

def test_graph_queries_get_graph_context(mock_neo4j):
    """Test getting graph context through GraphQueries"""
    mock_neo4j.run.return_value.single.return_value = {
        "entities": [{"name": "John Smith", "type": "Person"}],
        "relationships": []
    }
    
    queries = GraphQueries()
    result = asyncio.run(queries.get_graph_context(note_id=1, max_depth=2))
    
    assert "entities" in result
    assert "relationships" in result
    assert "context_summary" in result
    assert "query_time" in result

def test_graph_queries_get_entity_details(mock_neo4j):
    """Test getting entity details through GraphQueries"""
    mock_neo4j.run.return_value.single.return_value = {
        "entity": {"name": "John Smith", "type": "Person"},
        "relationships": [],
        "relationship_count": 0
    }
    
    queries = GraphQueries()
    result = asyncio.run(queries.get_entity_details("John Smith"))
    
    assert "entity" in result
    assert "relationships" in result
    assert "relationship_count" in result

def test_graph_queries_get_entity_details_not_found(mock_neo4j):
    """Test getting non-existent entity details through GraphQueries"""
    mock_neo4j.run.return_value.single.return_value = None
    
    queries = GraphQueries()
    with pytest.raises(Exception, match="Entity not found"):
        asyncio.run(queries.get_entity_details("NonExistent"))

def test_graph_queries_search_entities(mock_neo4j):
    """Test searching entities through GraphQueries"""
    mock_neo4j.run.return_value.data.return_value = [
        {"entity": {"name": "John Smith", "type": "Person"}, "relevance_score": 1.0}
    ]
    
    queries = GraphQueries()
    result = asyncio.run(queries.search_entities("John", limit=20))
    
    assert "results" in result
    assert "count" in result
    assert len(result["results"]) == 1

def test_graph_queries_get_graph_stats(mock_neo4j):
    """Test getting graph stats through GraphQueries"""
    mock_neo4j.run.return_value.single.side_effect = [
        {"total_nodes": 10, "entity_count": 8, "note_count": 2},
        {"total_relationships": 5, "relationship_types": 3}
    ]
    mock_neo4j.run.return_value.data.return_value = [
        {"entity_type": "Person", "count": 5}
    ]
    
    queries = GraphQueries()
    result = asyncio.run(queries.get_graph_stats())
    
    assert "total_nodes" in result
    assert "entity_count" in result
    assert "note_count" in result
    assert "total_relationships" in result
    assert "relationship_types" in result
    assert "entity_type_distribution" in result

def test_graph_queries_get_recommendations(mock_neo4j):
    """Test getting recommendations through GraphQueries"""
    mock_neo4j.run.return_value.data.return_value = [
        {
            "entity": {"name": "Sarah Johnson", "type": "Person"},
            "common_connections": 2,
            "relationship_types": ["WORKS_FOR"],
            "recommendation_score": 0.8
        }
    ]
    
    queries = GraphQueries()
    result = asyncio.run(queries.get_recommendations("John Smith", limit=10))
    
    assert "recommendations" in result
    assert "count" in result
    assert len(result["recommendations"]) == 1

def test_graph_queries_generate_context_summary():
    """Test context summary generation"""
    queries = GraphQueries()
    
    entities = [
        {"name": "John Smith", "type": "Person"},
        {"name": "Acme Corp", "type": "Organization"},
        {"name": "Project Alpha", "type": "Project"}
    ]
    relationships = [
        {"from": "John Smith", "to": "Acme Corp", "type": "WORKS_FOR"},
        {"from": "Project Alpha", "to": "John Smith", "type": "PART_OF_PROJECT"}
    ]
    
    summary = queries._generate_context_summary(entities, relationships)
    
    assert "Context includes:" in summary
    assert "1 Person: John Smith" in summary
    assert "1 Organization: Acme Corp" in summary
    assert "1 Project: Project Alpha" in summary
    assert "2 relationships" in summary

def test_graph_queries_generate_context_summary_empty():
    """Test context summary generation with empty entities"""
    queries = GraphQueries()
    
    entities = []
    relationships = []
    
    summary = queries._generate_context_summary(entities, relationships)
    
    assert "No entities found in context." in summary
