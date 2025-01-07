import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue dans l'API de classification des oiseaux"}

def test_predict():
    with open("test/test_image.png", "rb") as f:
        response = client.post("/predict/", files={"file": ("test/test_image.png", f, "image/png")})
    assert response.status_code == 200
    assert "prediction" in response.json()