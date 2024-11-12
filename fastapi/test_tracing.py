# test_tracing.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_find_word():
    word = "python"
    response = client.get(f"/find/{word}")
    assert response.status_code == 200
    # Add more specific assertions based on your expected results

def test_semantic_search():
    phrase = "machine learning"
    k = 3
    response = client.get(f"/search/{phrase}/{k}")
    assert response.status_code == 200
    assert len(response.json()) <= k
    # Add more specific assertions based on your expected results

if __name__ == "__main__":
    pytest.main([__file__])