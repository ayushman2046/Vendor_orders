import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    secret_token = os.getenv('AUTH_TOKEN')
    return {
        "Authorization": f"Bearer {secret_token}",
        "Content-Type": "application/json"
    }