import pytest
from uuid import uuid4
from app.models.users import Users
from app.core.security import create_access_token


def test_get_users(client, db):
    user1 = Users(id=uuid4(),
                  email="user1@example.com",
                  username="user1",
                  hashed_password="hashed_pwd1")
    user2 = Users(id=uuid4(), email="user2@example.com", username="user2",
                  hashed_password="hashed_pwd2")
    db.add(user1)
    db.add(user2)
    db.commit()
    token = create_access_token(data={"sub": user1.username})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


def test_get_user(client, db):
    user = Users(id=uuid4(),
                 email="user3@example.com",
                 username="user3",
                 hashed_password="hashed_pwd3")
    db.add(user)
    db.commit()
    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/users/{user.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user3@example.com"
    assert data["username"] == "user3"


def test_get_user_not_found(client, db):
    user = Users(id=uuid4(),
                 email="user@example.com",
                 username="testuser",
                 hashed_password="hashed_pwd")
    db.add(user)
    db.commit()
    non_existent_id = uuid4()
    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/users/{non_existent_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_user(client, db):
    user = Users(id=uuid4(),
                 email="user@example.com",
                 username="testuser",
                 hashed_password="hashed_pwd")
    db.add(user)
    db.commit()
    non_existent_id = uuid4()
    token = create_access_token(data={"sub": user.username})
    payload = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/users", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "hashed_password" not in data


def test_create_user_existing_email(client, db):
    user = Users(id=uuid4(),
                 email="existing@example.com",
                 username="existinguser",
                 hashed_password="hashed_pwd")
    db.add(user)
    db.commit()
    payload = {
        "email": "existing@example.com",
        "username": "newuser2",
        "password": "newpassword"
    }
    token = create_access_token(data={"sub": "existinguser"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/users", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_create_user_existing_username(client, db):
    user = Users(id=uuid4(),
                 email="unique@example.com",
                 username="existingusername",
                 hashed_password="hashed_pwd")
    db.add(user)
    db.commit()

    payload = {
        "email": "newunique@example.com",
        "username": "existingusername",
        "password": "newpassword"
    }
    token = create_access_token(data={"sub": "existingusername"})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/users", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_update_user(client, db):
    user = Users(id=uuid4(),
                 email="updateuser@example.com",
                 username="updateuser",
                 hashed_password="hashed_pwd")
    db.add(user)
    db.commit()
    payload = {
        "email": "updated@example.com",
        "password": "newhashedpassword"
    }
    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch(f"/api/v1/users/{user.id}", json=payload,
                            headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
