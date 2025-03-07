import asyncio
import pytest
from app.tests.conftest import delete_user


def test_register_user(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "phone": "+1987654321",
        "password": "newpassword"
    }
    response = client.post("api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == user_data["username"]


def test_register_user_existing_username(client):
    user_data = {
        "username": "newuser",
        "email": "newemail@example.com",
        "phone": "+1987654321",
        "password": "newpassword"
    }
    response = client.post("api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_login(client):
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    response = client.post("api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    login_data = {
        "username": "newuser",
        "password": "wrongpassword"
    }
    response = client.post("api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_me(client):
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post("api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    response = client.get(
        "api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"

@pytest.mark.asyncio
async def test_logout(client):
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post("api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    response = client.post(
        "api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

@pytest.mark.asyncio
async def test_delete_test_user():
    await delete_user('newuser')
    await asyncio.sleep(1)
