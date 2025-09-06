from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_health_ok():
    """Test health endpoint returns status ok"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok" 
    assert data["version"] == "1.0.0"

def test_map_single():
    """Test single record mapping with enrichment"""
    test_data = {
        "record": {
            "title": "Sony Headphones",
            "price": "99.99"
        }
    }
    response = client.post("/map/single", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "record" in data
    # Verify enrichment applied
    record = data["record"]
    assert "title" in record
    assert "brand" in record  # Should be enriched by pipeline

def test_map_batch_length():
    """Test batch mapping returns correct number of records"""
    test_data = {
        "records": [
            {"title": "Sony Headphones", "price": "99.99"},
            {"title": "Apple iPhone", "price": "699.99"}
        ]
    }
    response = client.post("/map", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data["records"]) == 2
    # Verify enrichment applied to first record
    assert "brand" in data["records"][0]

def test_map_single_empty_record():
    """Test error handling for empty record"""
    response = client.post("/map/single", json={"record": {}})
    assert response.status_code == 400
