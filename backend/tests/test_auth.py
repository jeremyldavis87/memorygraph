import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user(setup_database):
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword",
        "full_name": "New User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"

def test_register_duplicate_email(test_user):
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "anotheruser",
        "password": "password",
        "full_name": "Another User"
    })
    assert response.status_code == 400

def test_login_success(test_user):
    response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_current_user(test_user):
    # First login to get token
    login_response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    
    # Use token to get current user
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"