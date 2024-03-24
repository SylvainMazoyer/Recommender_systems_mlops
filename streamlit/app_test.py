import pytest
import requests


# Test du endpoint GET /
def test_get_test():
    response = requests.get("http://api_model_container:5000/").json()
    assert response == {'message': 'API is functional'}
