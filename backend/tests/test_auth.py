import pytest

def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "New User",
            "email": "new@example.com",
            "password": "StrongPassword123!",
            "role": "citizen"
        }
    )
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"

def test_register_existing_user(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Existing User",
            "email": test_user.email,
            "password": "StrongPassword123!",
            "role": "citizen"
        }
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_success(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "StrongPassword123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_read_users_me(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
