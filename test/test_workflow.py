import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_full_workflow():
    # Step 1: Predict an image
    with open("test_image.png", "rb") as f:
        predict_response = client.post("/predict/", files={"file": ("test_image.png", f, "image/png")})
    assert predict_response.status_code == 200
    prediction = predict_response.json().get("prediction")
    assert prediction is not None

    # Step 2: Retrieve images from the database
    images_response = client.get("/images/")
    assert images_response.status_code == 200
    assert isinstance(images_response.json(), list)
