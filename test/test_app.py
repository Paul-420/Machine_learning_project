from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API de classification des oiseaux !"}

def test_predict():
    with open("test_image.jpg", "rb") as img:
        response = client.post("/predict", files={"file": img})
        assert response.status_code == 200
