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

def test_predict_valid_image():
    with open("test_image.png", "rb") as image_file:  # Assurez-vous d'avoir une image pour les tests
        response = client.post("/predict/", files={"file": ("test_image.png", image_file, "image/jpeg")})
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_predict_invalid_image():
    with open("test_image.txt", "rb") as invalid_file:  # Fichier texte pour tester une image invalide
        response = client.post("/predict/", files={"file": ("test_image.txt", invalid_file, "text/plain")})
    assert response.status_code == 422  # Attendre un code d'erreur pour une mauvaise image
    assert "error" in response.json()

