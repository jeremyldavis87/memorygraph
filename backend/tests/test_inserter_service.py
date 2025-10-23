import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add the graph services to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'graph-services', 'inserter-service'))

from app.main import app as inserter_app
from app.db.neo4j_client import Neo4jClient

inserter_client = TestClient(inserter_app)

@pytest.fixture
def mock_neo4j():
    """Mock Neo4j driver for testing"""
    with patch('app.db.neo4j_client.AsyncGraphDatabase.driver') as mock_driver:
        mock_session = AsyncMock()
        mock_driver.return_value.session.return_value.__aenter__.return_value = mock_session
        yield mock_session

def test_inserter_health_check(mock_neo4j):
    """Test inserter service health endpoint"""
    # Mock successful connection test
    mock_neo4j.run.return_value.single.return_value = {"test": 1}
    
    response = inserter_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "inserter"
    assert data["neo4j"] == "connected"

def test_inserter_health_check_failure():
    """Test inserter service health endpoint when Neo4j is down"""
    with patch('app.db.neo4j_client.AsyncGraphDatabase.driver') as mock_driver:
        mock_driver.side_effect = Exception("Connection failed")
        
        response = inserter_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["neo4j"] == "disconnected"

def test_insert_triples(mock_neo4j):
    """Test inserting triples"""
    # Mock successful insertion
    mock_neo4j.run.return_value.single.return_value = {"action": "created"}
    
    response = inserter_client.post("/insert", json={
        "triples": [
            {
                "subject": "John Smith",
                "predicate": "WORKS_FOR",
                "object": "Acme Corp",
                "confidence": 0.9,
                "entity_type": "Person",
                "relationship_type": "WORKS_FOR",
                "properties": {}
            }
        ],
        "note_id": 1,
        "user_id": 1
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "inserted_count" in data
    assert "merged_count" in data
    assert "errors" in data
    assert "processing_time" in data

def test_bulk_insert_triples(mock_neo4j):
    """Test bulk inserting triples"""
    # Mock successful bulk insertion
    mock_neo4j.run.return_value.single.return_value = {"total_relationships": 5}
    
    response = inserter_client.post("/bulk-insert", json={
        "triples": [
            {
                "subject": "John Smith",
                "predicate": "WORKS_FOR",
                "object": "Acme Corp",
                "confidence": 0.9,
                "entity_type": "Person",
                "relationship_type": "WORKS_FOR",
                "properties": {}
            },
            {
                "subject": "Project Alpha",
                "predicate": "PART_OF_PROJECT",
                "object": "John Smith",
                "confidence": 0.8,
                "entity_type": "Project",
                "relationship_type": "PART_OF_PROJECT",
                "properties": {}
            }
        ],
        "note_id": 1,
        "user_id": 1,
        "batch_size": 100
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "inserted_count" in data
    assert "merged_count" in data
    assert "errors" in data
    assert "processing_time" in data

def test_merge_entity(mock_neo4j):
    """Test merging an entity"""
    # Mock successful merge
    mock_neo4j.run.return_value.single.return_value = {
        "e": {"id": "123", "name": "John Smith", "type": "Person"},
        "action": "created"
    }
    
    response = inserter_client.post("/merge-entity", json={
        "entity_name": "John Smith",
        "entity_type": "Person",
        "properties": {"role": "Developer"},
        "merge_strategy": "merge"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "entity_id" in data
    assert "action" in data
    assert "properties" in data
    assert data["action"] == "created"

def test_get_entity(mock_neo4j):
    """Test getting an entity"""
    # Mock successful entity retrieval
    mock_neo4j.run.return_value.single.return_value = {
        "e": {"name": "John Smith", "type": "Person"},
        "relationships": [
            {
                "relationship": "WORKS_FOR",
                "direction": "outgoing",
                "target": "Acme Corp",
                "properties": {}
            }
        ]
    }
    
    response = inserter_client.get("/entity/John Smith")
    
    assert response.status_code == 200
    data = response.json()
    assert "entity" in data
    assert "relationships" in data
    assert data["entity"]["name"] == "John Smith"

def test_get_entity_not_found(mock_neo4j):
    """Test getting a non-existent entity"""
    # Mock entity not found
    mock_neo4j.run.return_value.single.return_value = None
    
    response = inserter_client.get("/entity/NonExistent")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]

def test_delete_entity(mock_neo4j):
    """Test deleting an entity"""
    # Mock successful deletion
    mock_neo4j.run.return_value.single.return_value = {"deleted_relationships": 3}
    
    response = inserter_client.delete("/entity/John Smith")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "relationships_deleted" in data
    assert data["relationships_deleted"] == 3

def test_get_graph_stats(mock_neo4j):
    """Test getting graph statistics"""
    # Mock stats queries
    mock_neo4j.run.return_value.single.side_effect = [
        {"node_count": 10, "entity_count": 8, "note_count": 2},
        {"total_relationships": 5, "relationship_types": 3}
    ]
    mock_neo4j.run.return_value.data.return_value = [
        {"entity_type": "Person", "count": 5},
        {"entity_type": "Organization", "count": 3}
    ]
    
    response = inserter_client.get("/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_nodes" in data
    assert "entity_count" in data
    assert "note_count" in data
    assert "total_relationships" in data
    assert "relationship_types" in data
    assert "entity_types" in data

def test_neo4j_client_initialization():
    """Test Neo4jClient initialization"""
    with patch.dict(os.environ, {
        'NEO4J_URI': 'neo4j://localhost:7687',
        'NEO4J_USERNAME': 'neo4j',
        'NEO4J_PASSWORD': 'password',
        'NEO4J_DATABASE': 'neo4j'
    }):
        client = Neo4jClient()
        assert client.uri == 'neo4j://localhost:7687'
        assert client.username == 'neo4j'
        assert client.password == 'password'
        assert client.database == 'neo4j'

def test_neo4j_client_test_connection(mock_neo4j):
    """Test Neo4j connection test"""
    mock_neo4j.run.return_value.single.return_value = {"test": 1}
    
    client = Neo4jClient()
    result = asyncio.run(client.test_connection())
    assert result is True

def test_neo4j_client_test_connection_failure():
    """Test Neo4j connection test failure"""
    with patch('app.db.neo4j_client.AsyncGraphDatabase.driver') as mock_driver:
        mock_driver.side_effect = Exception("Connection failed")
        
        client = Neo4jClient()
        with pytest.raises(Exception, match="Neo4j connection failed"):
            asyncio.run(client.test_connection())

def test_neo4j_client_insert_triples(mock_neo4j):
    """Test inserting triples through Neo4jClient"""
    mock_neo4j.run.return_value.single.return_value = {"action": "created"}
    
    client = Neo4jClient()
    triples = [
        {
            "subject": "John Smith",
            "predicate": "WORKS_FOR",
            "object": "Acme Corp",
            "confidence": 0.9,
            "entity_type": "Person",
            "relationship_type": "WORKS_FOR",
            "properties": {}
        }
    ]
    
    result = asyncio.run(client.insert_triples(triples, note_id=1, user_id=1))
    
    assert "inserted_count" in result
    assert "merged_count" in result
    assert "errors" in result
    assert "processing_time" in result

def test_neo4j_client_merge_entity(mock_neo4j):
    """Test merging entity through Neo4jClient"""
    mock_neo4j.run.return_value.single.return_value = {
        "e": {"id": "123", "name": "John Smith", "type": "Person"},
        "action": "created"
    }
    
    client = Neo4jClient()
    result = asyncio.run(client.merge_entity(
        name="John Smith",
        entity_type="Person",
        properties={"role": "Developer"},
        strategy="merge"
    ))
    
    assert "entity_id" in result
    assert "action" in result
    assert "properties" in result

def test_neo4j_client_get_entity(mock_neo4j):
    """Test getting entity through Neo4jClient"""
    mock_neo4j.run.return_value.single.return_value = {
        "e": {"name": "John Smith", "type": "Person"},
        "relationships": []
    }
    
    client = Neo4jClient()
    result = asyncio.run(client.get_entity("John Smith"))
    
    assert "entity" in result
    assert "relationships" in result
    assert result["entity"]["name"] == "John Smith"

def test_neo4j_client_get_entity_not_found(mock_neo4j):
    """Test getting non-existent entity through Neo4jClient"""
    mock_neo4j.run.return_value.single.return_value = None
    
    client = Neo4jClient()
    with pytest.raises(Exception, match="Entity not found"):
        asyncio.run(client.get_entity("NonExistent"))

def test_neo4j_client_delete_entity(mock_neo4j):
    """Test deleting entity through Neo4jClient"""
    mock_neo4j.run.return_value.single.return_value = {"deleted_relationships": 2}
    
    client = Neo4jClient()
    result = asyncio.run(client.delete_entity("John Smith"))
    
    assert result == 2

def test_neo4j_client_get_graph_stats(mock_neo4j):
    """Test getting graph stats through Neo4jClient"""
    mock_neo4j.run.return_value.single.side_effect = [
        {"node_count": 10, "entity_count": 8, "note_count": 2},
        {"total_relationships": 5, "relationship_types": 3}
    ]
    mock_neo4j.run.return_value.data.return_value = [
        {"entity_type": "Person", "count": 5}
    ]
    
    client = Neo4jClient()
    result = asyncio.run(client.get_graph_stats())
    
    assert "total_nodes" in result
    assert "entity_count" in result
    assert "note_count" in result
    assert "total_relationships" in result
    assert "relationship_types" in result
    assert "entity_type_distribution" in result
