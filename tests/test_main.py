import os
import pytest
from fastapi.testclient import TestClient

# 테스트용 환경변수 설정
os.environ["K8S_TOKEN"] = "test-token"
os.environ["K8S_API"] = "https://test-api:6443"
os.environ["VERIFY_SSL"] = "false"

from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Kubernetes Dashboard API"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
