import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_get_images():
    response = client.get("/images/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_image():
    response = client.get("/images/1")
    assert response.status_code in [200, 404]
