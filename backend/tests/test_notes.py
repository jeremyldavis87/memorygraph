import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers(test_user):
    # Login to get token
    response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_note(auth_headers):
    response = client.post("/api/v1/notes/", json={
        "title": "Test Note",
        "content": "This is a test note",
        "source_type": "rocketbook"
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note"

def test_get_notes(auth_headers):
    # Create a note first
    client.post("/api/v1/notes/", json={
        "title": "Test Note",
        "content": "This is a test note",
        "source_type": "rocketbook"
    }, headers=auth_headers)
    
    response = client.get("/api/v1/notes/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert len(data["notes"]) >= 1

def test_get_note_by_id(auth_headers):
    # Create a note first
    create_response = client.post("/api/v1/notes/", json={
        "title": "Test Note",
        "content": "This is a test note",
        "source_type": "rocketbook"
    }, headers=auth_headers)
    
    note_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"

def test_update_note(auth_headers):
    # Create a note first
    create_response = client.post("/api/v1/notes/", json={
        "title": "Test Note",
        "content": "This is a test note",
        "source_type": "rocketbook"
    }, headers=auth_headers)
    
    note_id = create_response.json()["id"]
    
    response = client.put(f"/api/v1/notes/{note_id}", json={
        "title": "Updated Note",
        "content": "This is an updated note"
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Note"
    assert data["content"] == "This is an updated note"

def test_delete_note(auth_headers):
    # Create a note first
    create_response = client.post("/api/v1/notes/", json={
        "title": "Test Note",
        "content": "This is a test note",
        "source_type": "rocketbook"
    }, headers=auth_headers)
    
    note_id = create_response.json()["id"]
    
    response = client.delete(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify note is deleted
    get_response = client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert get_response.status_code == 404