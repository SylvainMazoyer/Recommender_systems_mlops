from fastapi.testclient import TestClient 
from src.api.main import api
import pytest

client = TestClient(api)

# Test du endpoint GET /test
def test_get_test():
    assert client.get("/test").status_code == 200
    assert client.get("/test").json() == {'message': 'API is functional'}

# Test du endpoint GET /secure-data/
def test_get_secure_data():
    assert client.get("/secure-data/", headers={"Authorization": "Basic YWRtaWGRtMU4="}).status_code == 401
    assert client.get("/secure-data/", headers={"Authorization": "Basic YWRtaW46ZGF0YXNjaWVudGVzdA=="}).status_code == 200
