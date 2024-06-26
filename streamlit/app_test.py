import pytest
import requests
import os
import psycopg2


# Test du endpoint GET /
def test_get_test():
    response = requests.get("http://api_model_container:5000/").json()
    assert response == {'message': 'API is functional'}


# Test with valid credentials and requested role 'Data'
def test_get_secure_data_with_valid_credentials_and_data_role():
    response = requests.get("http://api_model_container:5000/admin/Data", 
                            auth=('Yousra', str(os.getenv('YOUSRA_PASSWORD')))).json()
    assert response == {'message' : "Bonjour Yousra, vous êtes connecté(e) en tant qu'administrateur"}

# Test with valid credentials and requested role other than 'Data'
def test_get_secure_data_with_valid_credentials_and_other_role():
    response = requests.get("http://api_model_container:5000/admin/Data", 
                            auth=('Dataflix', str(os.getenv('DATAFLIX_PASSWORD')))).json()
    print(response)
    assert response['detail'] == 'Droits insuffisants'


# Test with invalid credentials
def test_get_secure_data_with_invalid_credentials():
    response = requests.get("http://api_model_container:5000/admin/Data", 
                            auth=('invalid_username', 'invalid_password')).json()
    assert response['detail'] == 'Utilisateur inconnu'

# Test with correct username but incorrect password
def test_get_secure_data_with_correct_username_but_incorrect_password():
    response = requests.get("http://api_model_container:5000/admin/Data", 
                            auth=('Yousra', 'invalid_password')).json()
    assert response['detail'] == 'Mot de passe incorrect'

# Test creating a new user
def test_create_user():
    # Send a POST request to create a new user
    response = requests.post("http://api_model_container:5000/create-user", json={"name": "new_user"})
    data = response.json()

    conn = psycopg2.connect(
        dbname='dataflix',
        user='postgres',
        password='dataflix',
        host='data_container', 
        port='5432'
    )

    cur = conn.cursor()
    cur.execute("SELECT * FROM utilisateurs where name_user='new_user'")
    rows = cur.fetchone()
    cur.close()
    conn.close()

    # Assert that the response indicates the user was created successfully
    assert response.status_code == 200
    assert data['message'] == "user created successfully"
    assert 'userId' in data
    assert rows

# Test attempting to create a user that already exists
def test_create_existing_user():
    # Send a POST request to create a user that already exists
    response = requests.post("http://api_model_container:5000/create-user", json={"name": "user1"})
    data = response.json()

    # Assert that the response indicates the user already exists
    assert response.status_code == 200
    assert data['message'] == "user already exists"



    
