import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue dans l'API de classification des oiseaux"}

def test_get_images():
    response = client.get("/images/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Vérifie que la réponse est une liste
    if data:  # Vérifie si la liste n'est pas vide
        assert "id" in data[0]
        assert "class_label" in data[0]
        assert "image" in data[0]

