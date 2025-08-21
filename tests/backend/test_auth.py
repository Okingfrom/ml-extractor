"""
Test authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "ML Extractor API" in data["message"]

def test_register_user(client: TestClient):
    """Test user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPassword123"
    }
    
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "registered successfully" in data["message"]

def test_register_duplicate_user(client: TestClient):
    """Test registering duplicate user"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPassword123"
    }
    
    # Register first user
    client.post("/api/auth/register", json=user_data)
    
    # Try to register same user again
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400

def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent user"""
    login_data = {
        "username": "nonexistent",
        "password": "password"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401

def test_invalid_password_format(client: TestClient):
    """Test registration with invalid password"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "weak"  # Too short, no uppercase, no digits
    }
    
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 422  # Validation error
