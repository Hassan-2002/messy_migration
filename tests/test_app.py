import pytest
import os
import sqlite3
from app import create_app
from init_db import init_db
from werkzeug.security import generate_password_hash

TEST_DATABASE_PATH = 'instance/test_users.db'

@pytest.fixture(scope='session', autouse=True)
def set_test_env():
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_PATH'] = TEST_DATABASE_PATH
    os.environ['SECRET_KEY'] = 'test_secret_key'
    yield
    del os.environ['FLASK_ENV']
    del os.environ['DATABASE_PATH']
    del os.environ['SECRET_KEY']
    if os.path.exists(TEST_DATABASE_PATH):
        os.remove(TEST_DATABASE_PATH)


@pytest.fixture
def app():
    if os.path.exists(TEST_DATABASE_PATH):
        os.remove(TEST_DATABASE_PATH)

    init_db()

    app = create_app('testing')
    app.config['TESTING'] = True

    yield app


@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"status": "ok", "message": "User API is operational!"}

def test_create_user_success(client):
    response = client.post('/users', json={
        'name': 'testuser',
        'email': 'test@example.com',
        'password': 'strongpassword123'
    })
    assert response.status_code == 201
    assert response.json['message'] == "User created successfully"
    assert 'id' in response.json

def test_create_user_validation_error(client):
    response = client.post('/users', json={
        'name': 'shortpassuser',
        'email': 'short@example.com',
        'password': 'short'
    })
    assert response.status_code == 400
    assert response.json['message'] == "Validation error"
    assert 'payload' in response.json

def test_create_user_duplicate_username(client):
    client.post('/users', json={
        'name': 'duplicateuser',
        'email': 'dup@example.com',
        'password': 'password123'
    })
    response = client.post('/users', json={
        'name': 'duplicateuser',
        'email': 'another@example.com',
        'password': 'password123'
    })
    assert response.status_code == 409
    assert response.json['message'] == "User with name 'duplicateuser' already exists"

def test_get_all_users(client):
    response = client.get('/users')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any(user['name'] == 'admin' for user in response.json)

def test_get_specific_user_success(client):
    create_response = client.post('/users', json={
        'name': 'specificuser',
        'email': 'specific@example.com',
        'password': 'password123'
    })
    user_id = create_response.json['id']

    response = client.get(f'/user/{user_id}')
    assert response.status_code == 200
    assert response.json['id'] == user_id
    assert response.json['name'] == 'specificuser'

def test_get_specific_user_not_found(client):
    response = client.get('/user/99999')
    assert response.status_code == 404
    assert response.json['message'] == "User not found"

def test_login_success(client):
    response = client.post('/login', json={
        'name': 'admin',
        'password': 'adminpass'
    })
    assert response.status_code == 200
    assert response.json['message'] == "Login successful"
    assert 'user_id' in response.json

def test_login_invalid_credentials(client):
    response = client.post('/login', json={
        'name': 'admin',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json['message'] == "Invalid name or password"

def test_update_user_success(client):
    create_response = client.post('/users', json={
        'name': 'user_to_update',
        'email': 'update@example.com',
        'password': 'oldpassword'
    })
    user_id = create_response.json['id']

    response = client.put(f'/user/{user_id}', json={
        'name': 'updated_user_name',
        'email': 'updated_email@example.com'
    })
    assert response.status_code == 200
    assert response.json['message'] == "User updated successfully"

    get_response = client.get(f'/user/{user_id}')
    assert get_response.json['name'] == 'updated_user_name'
    assert get_response.json['email'] == 'updated_email@example.com'

def test_delete_user_success(client):
    create_response = client.post('/users', json={
        'name': 'user_to_delete',
        'email': 'delete@example.com',
        'password': 'password123'
    })
    user_id = create_response.json['id']

    response = client.delete(f'/user/{user_id}')
    assert response.status_code == 204

    get_response = client.get(f'/user/{user_id}')
    assert get_response.status_code == 404
