from fastapi.testclient import TestClient 
from src.api.main import api
import pytest

client = TestClient(api)


def test_get_test():
    assert client.get("/test").status_code == 200
    assert client.get("/test").json() == {'message': 'API is functional'}


