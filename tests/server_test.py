from fastapi import FastAPI
from fastapi.testclient import TestClient

from briq_api.server import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.text == '"ok"'
