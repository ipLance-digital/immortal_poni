import os
import tempfile
from uuid import UUID
import pytest
from app.tests.conftest import delete_user

@pytest.mark.asyncio
async def test_register_user(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "phone": "+1987654321",
        "password": "newpassword"
    }
    response = client.post("api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == user_data["username"]

@pytest.mark.asyncio
async def test_upload_file(client):
    file_content = b"Test file content"
    with tempfile.NamedTemporaryFile(dir="", delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post(
        "api/v1/auth/login",
        json=login_data
    )
    cookies = {
        "access_token": login_response.cookies.get("access_token"),
        "refresh_token": login_response.cookies.get("refresh_token"),
        "csrf_token": login_response.cookies.get("csrf_token")
    }
    assert login_response.status_code == 200
    with open(tmp_path, "rb") as file:
        response = client.post(
            "api/v1/storage/upload",
            files={
                "file": (
                    os.path.basename(tmp_path),
                    file,
                    "application/octet-stream"
                )
            },
            cookies=cookies,
            headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
        )
    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"]
    file_id = response_data["message"]
    response = client.delete(
        f"api/v1/storage/delete/{UUID(file_id)}",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
    )
    assert response.status_code == 200
    os.remove(tmp_path)
    response = client.post(
        "api/v1/auth/logout",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_rename_file(client):
    new_name = "new_name"
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post(
        "api/v1/auth/login",
        json=login_data,
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
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
    )
    user_id = response.json()['id']
    file_content = b"Test file content"
    with tempfile.NamedTemporaryFile(dir="", delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    with open(tmp_path, "rb") as file:
        response = client.post(
            "api/v1/storage/upload",
            files={
                "file": (
                    os.path.basename(tmp_path),
                    file,
                    "application/octet-stream"
                )
            },
            cookies=cookies,
            headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
        )
    assert response.status_code == 200
    file_id = response.json()['message']
    response = client.patch(
        f"api/v1/storage/rename/{UUID(file_id)}?new_name={new_name}",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
    )
    assert response.status_code == 200
    response = client.delete(
        f"api/v1/storage/delete/{UUID(file_id)}",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
    )
    assert "message" in response.json()
    response = client.post(
        "api/v1/auth/logout",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
    )
    assert response.status_code == 200
    os.remove(tmp_path)

@pytest.mark.asyncio
async def test_delete_file(client):
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
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
    )
    file_content = b"Test file content"
    with tempfile.NamedTemporaryFile(dir="", delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    with open(tmp_path, "rb") as file:
        response = client.post(
            "api/v1/storage/upload",
            files={
                "file": (
                    os.path.basename(tmp_path),
                    file,
                    "application/octet-stream"
                )
            },
            cookies=cookies,
            headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
        )
    assert response.status_code == 200
    file_id = response.json()['message']
    response = client.delete(
        f"api/v1/storage/delete/{UUID(file_id)}",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
    )
    assert response.status_code == 200
    assert "message" in response.json()
    response = client.post(
        "api/v1/auth/logout",
        cookies=cookies,
        headers={"X-CSRF-TOKEN": login_response.cookies.get("csrf_token")},
    )
    assert response.status_code == 200
    os.remove(tmp_path)

@pytest.mark.asyncio
async def test_delete_test_user():
    await delete_user('newuser')
