import pytest
import requests

# Test du endpoint GET /
def test_get_test():
    response = requests.get("http://api_model_container:5000/").json()
    assert response == {'message': 'API is functional'}


# Test with valid credentials and requested role 'Data'
def test_get_secure_data_with_valid_credentials_and_data_role():
    response = requests.get("http://api_model_container:5000/admin/Data", 
                            auth=('Yousra', '$2b$12$SU3tZD.1hiB.CP3Y.3d23eDu0Ch1EgCt.4CmfSiLW7UGeNjmWnmOe')).json()
    assert response['message'] == "Hello Yousra, you have access to secure data"

# Test with valid credentials and requested role other than 'Data'
def test_get_secure_data_with_valid_credentials_and_other_role():
    response = requests.get("http://api_model_container:5000/admin/Plateforme", 
                            auth=('Dataflix', '$2b$12$63F7IpKFNbuWx1vi08p/Ie9RDuqJsQZ.BOyc3HguQkgzZsBhY50U.')).json()
    assert response['detail'] == 'Droits insuffisants'
    assert response['status_code'] == 401
    assert 'WWW-Authenticate' in response['headers']

# Test with invalid credentials
def test_get_secure_data_with_invalid_credentials():
    response = requests.get("http://api_model_container:5000/admin/Data", 
                            auth=('invalid_username', 'invalid_password')).json()
    assert response['detail'] == 'Utilisateur inconnu'
    assert response['status_code'] == 401
    assert 'WWW-Authenticate' in response['headers']

# Test with correct username but incorrect password
def test_get_secure_data_with_correct_username_but_incorrect_password():
    response = requests.get("http://api_model_container:5000/admin/Data", 
                            auth=('Yousra', 'invalid_password')).json()
    assert response['detail'] == 'Mot de passe incorrect'
    assert response['status_code'] == 401
    assert 'WWW-Authenticate' in response['headers']
    
# Test creating a new user
def test_create_user():
    # Send a POST request to create a new user
    response = requests.post("http://api_model_container:5000/create-user", json={"name": "new_user"})
    data = response.json()

    # Assert that the response indicates the user was created successfully
    assert response.status_code == 200
    assert data['message'] == "user created successfully"
    assert 'userId' in data

# Test attempting to create a user that already exists
def test_create_existing_user():
    # Send a POST request to create a user that already exists
    response = requests.post("http://api_model_container:5000/create-user", json={"name": "user_1"})
    data = response.json()

    # Assert that the response indicates the user already exists
    assert response.status_code == 200
    assert data['message'] == "user already exists"
    assert 'userId' == 1


