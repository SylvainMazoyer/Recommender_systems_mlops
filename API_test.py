from fastapi.testclient import TestClient 
from src.api.main import api
import pytest

client = TestClient(api)

# Test du endpoint GET /
def test_get_test():
    assert client.get("/").status_code == 200
    assert client.get("/").json() == {'message': 'API is functional'}

# Test du endpoint GET /admin/
def test_get_admin():
    assert client.get("/admin", headers={"Authorization": "Basic YWRtaWGRtMU4="}).status_code == 401
    assert client.get("/admin", headers={"Authorization": "Basic cGxhdGVmb3JtZToxMjM="}).status_code == 200
    assert client.get("/admin", headers={"Authorization": "Basic ZXF1aXBlX2RzOjEyMw=="}).status_code == 200

# Test du endpoint GET /equipe_ds
def test_get_ds():
    assert client.get("/equipe_ds", headers={"Authorization": "Basic YWRtaWGRtMU4="}).status_code == 401
    assert client.get("/equipe_ds", headers={"Authorization": "Basic cGxhdGVmb3JtZToxMjM="}).status_code == 403
    assert client.get("/equipe_ds", headers={"Authorization": "Basic ZXF1aXBlX2RzOjEyMw=="}).status_code == 200

