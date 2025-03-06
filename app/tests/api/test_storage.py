import os
import tempfile
from uuid import uuid4


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


def test_upload_file(client):
    """Test file upload."""
    file_content = b"Test file content"
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post("api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Открываем файл перед отправкой в запрос
    with open(tmp_path, "rb") as file:
        response = client.post(
            "api/v1/storage/upload",
            files={"file": (
            os.path.basename(tmp_path), file, "application/octet-stream")},
            headers={"Authorization": f"Bearer {access_token}"}
        )

    assert response.status_code == 200
    response_data = response.json()
    assert "message" in response_data
    assert "file_id" in response_data[
        "message"]
    os.remove(tmp_path)


def test_delete_file(client):
    """Test file deletion."""
    file_id = uuid4()
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post("api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    response = client.delete(
        f"api/v1/storage/delete/{file_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert "message" in response.json()


def test_rename_file(client):
    """Test file renaming."""
    file_id = uuid4()
    new_name = "new_name.txt"
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post("api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    response = client.patch(
        f"api/v1/storage/rename/{file_id}",
        json={"new_name": new_name},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
