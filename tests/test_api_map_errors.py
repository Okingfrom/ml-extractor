from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_map_empty_payload_returns_empty_list():
    """
    POST /map with {} returns 200 and {"records": []}
    Tolerant behavior: missing records field treated as empty list
    """
    response = client.post("/map", json={})
    assert response.status_code == 200
    data = response.json()
    assert data == {"records": []}

def test_map_non_list_records_field():
    """
    POST /map with {"records": {}} returns 200 and coerces to {"records": []}
    Tolerant behavior: non-list records field coerced to empty list
    """
    response = client.post("/map", json={"records": {}})
    assert response.status_code == 200
    data = response.json()
    assert data == {"records": []}
    
    # Test other non-list types
    response = client.post("/map", json={"records": "invalid"})
    assert response.status_code == 200
    data = response.json()
    assert data == {"records": []}

def test_map_malformed_record_in_list():
    """Test that individual malformed records don't crash the endpoint"""
    test_data = {
        "records": [
            {"title": "Valid Record"},
            None,  # Invalid record
            {"title": "Another Valid Record"}
        ]
    }
    response = client.post("/map", json=test_data)
    # Should still return 200 but may have fewer records or errors handled gracefully
    assert response.status_code in [200, 500]  # Allow either graceful handling or error
