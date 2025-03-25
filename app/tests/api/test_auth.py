import pytest
import asyncio
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
    response_data = response.json()
    assert response_data["username"] == user_data["username"]
    assert response_data["email"] == user_data["email"]


def test_register_user_existing_username(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "phone": "+1987654321",
        "password": "newpassword"
    }
    response = client.post("api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_login(client):
    # логин по юзернэйму
    login_data_username = {
        "username": "newuser",
        "password": "newpassword"
    }
    response = client.post("api/v1/auth/login", json=login_data_username)
    assert response.status_code == 200
    response_data = response.json()
    assert "username" in response_data
    assert "newuser" == response_data.get("username")
    cookies = {
            "access_token": response.cookies.get("access_token"),
            "refresh_token": response.cookies.get("refresh_token"),
            "csrf_token": response.cookies.get("csrf_token")
    }
    client.post(
        "api/v1/auth/logout",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": response.cookies.get("csrf_token")},
    )
    # логин по эмеэйлу
    login_data_email = {
        "email": "newuser@example.com",
        "password": "newpassword"
    }
    response = client.post("api/v1/auth/login", json=login_data_email)
    assert response.status_code == 200
    response_data = response.json()
    assert "newuser@example.com" in response_data.get("email")
    cookies = {
            "access_token": response.cookies.get("access_token"),
            "refresh_token": response.cookies.get("refresh_token"),
            "csrf_token": response.cookies.get("csrf_token")
    }
    client.post(
        "api/v1/auth/logout",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": response.cookies.get("csrf_token")},
    )

    # логин по телефону
    phone_data_email = {
        "phone": "+1987654321",
        "password": "newpassword"
    }
    response = client.post("api/v1/auth/login", json=phone_data_email)
    assert response.status_code == 200
    response_data = response.json()
    assert "+1987654321" == response_data.get("phone")
    cookies = {
            "access_token": response.cookies.get("access_token"),
            "refresh_token": response.cookies.get("refresh_token"),
            "csrf_token": response.cookies.get("csrf_token")
    }
    client.post(
        "api/v1/auth/logout",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": response.cookies.get("csrf_token")},
    )


def test_login_invalid_credentials(client):
    login_data = {
        "username": "newuser",
        "password": "wrongpassword"
    }
    response = client.post("api/v1/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_me(client):
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post(
        "api/v1/auth/login",
        json=login_data
    )
    assert login_response.status_code == 200
    cookies = {
            "access_token": login_response.cookies.get("access_token"),
            "refresh_token": login_response.cookies.get("refresh_token"),
            "csrf_token": login_response.cookies.get("csrf_token")
    }
    response = client.get(
        "api/v1/auth/me",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["username"] == "newuser"
    assert "email" in response_data
    assert "id" in response_data

@pytest.mark.asyncio
async def test_logout(client):
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post("api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    assert login_response.status_code == 200
    cookies = {
            "access_token": login_response.cookies.get("access_token"),
            "refresh_token": login_response.cookies.get("refresh_token"),
            "csrf_token": login_response.cookies.get("csrf_token")
    }
    response = client.post(
        "api/v1/auth/logout",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


@pytest.mark.asyncio
async def test_delete_test_user():
    await delete_user('newuser')
    await asyncio.sleep(1)
