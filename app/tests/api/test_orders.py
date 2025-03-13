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
async def test_create_order(client):
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post(
        "api/v1/auth/login",
        json=login_data
    )
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    response = client.get(
        "api/v1/auth/me",
        cookies={"access_token": access_token}
    )
    user_id = response.json()['id']
    order_data = {
        "name": "New Order",
        "body": "Order details",
        "price": 100,
        "status": 1,
        "assign_to": user_id,
        "deadline": "2050-01-01T10:11:50",
    }
    response = client.post(
        "api/v1/orders/create",
        json=order_data,
        cookies={"access_token": access_token}
    )
    assert response.status_code == 200
    assert response.json()["name"] == order_data["name"]
    order_id = response.json()["id"]
    response = client.delete(
        f"api/v1/orders/delete_order/{UUID(order_id)}",
        cookies={"access_token": access_token}
    )
    assert response.status_code == 200
    assert "deleted" in response.json()


@pytest.mark.asyncio
async def test_attach_file_to_order(client):
    file_content = b"Test file content"
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
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
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    response = client.get(
        "api/v1/auth/me",
        cookies={"access_token": access_token}
    )
    user_id = response.json()['id']
    order_data = {
        "name": "New Order with File",
        "body": "Order details with file",
        "price": 100,
        "status": 1,
        "assign_to": user_id,
        "deadline": "2050-01-01T10:11:50",
    }
    order_response = client.post(
        "api/v1/orders/create",
        json=order_data,
        cookies={"access_token": access_token}
    )
    order_id = order_response.json()["id"]
    with open(tmp_path, "rb") as file:
        response = client.post(
            f"api/v1/orders/{UUID(order_id)}/attach_file",
            files={"file": (
            os.path.basename(tmp_path), file, "application/octet-stream")},
            cookies={"access_token": access_token} 
        )
    assert response.status_code == 200
    file_id = response.json()["file_id"]
    response = client.delete(
        f"api/v1/orders/{UUID(order_id)}/delete_file/{UUID(file_id)}",
        cookies={"access_token": access_token}
    )
    assert response.status_code == 200
    os.remove(tmp_path)


@pytest.mark.asyncio
async def test_update_order(client):
    update_data = {
        "price": 200,
    }

    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post(
        "api/v1/auth/login",
        json=login_data
    )
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    response = client.get(
        "api/v1/auth/me",
        cookies={"access_token": access_token} 
    )
    user_id = response.json()['id']
    order_data = {
        "name": "New Order to Update",
        "body": "Order details",
        "price": 150,
        "status": 1,
        "assign_to": user_id,
        "deadline": "2050-01-01T10:11:50",
    }
    order_response = client.post(
        "api/v1/orders/create",
        json=order_data,
        cookies={"access_token": access_token} 
    )
    order_id = order_response.json()["id"]
    response = client.patch(
        f"api/v1/orders/update_order/{UUID(order_id)}",
        json=update_data,
        cookies={"access_token": access_token} 
    )
    assert response.status_code == 200
    assert response.json()["price"] == update_data["price"]


@pytest.mark.asyncio
async def test_delete_order(client):
    login_data = {
        "username": "newuser",
        "password": "newpassword"
    }
    login_response = client.post(
        "api/v1/auth/login",
        json=login_data
    )
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("access_token")
    response = client.get(
        "api/v1/auth/me",
        cookies={"access_token": access_token} 
    )
    user_id = response.json()['id']
    order_data = {
        "name": "Order to Delete",
        "body": "Order details",
        "price": 100,
        "status": 1,
        "assign_to": user_id,
        "deadline": "2050-01-01T10:11:50",
    }
    order_response = client.post(
        "api/v1/orders/create",
        json=order_data,
        cookies={"access_token": access_token} 
    )
    order_id = order_response.json()["id"]
    response = client.delete(
        f"api/v1/orders/delete_order/{UUID(order_id)}",
        cookies={"access_token": access_token} 
    )
    assert response.status_code == 200
    assert "deleted" in response.json()


@pytest.mark.asyncio
async def test_delete_test_user():
    await delete_user('newuser')
