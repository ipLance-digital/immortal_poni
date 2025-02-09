import pytest
from uuid import uuid4
from app.models.users import Users
from app.core.security import get_password_hash


def test_register(client, db):
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"

def test_register_existing_email(client, db):
    user = Users(id=uuid4(), email="duplicate@example.com", username="uniqueuser", hashed_password="hashed_pwd")
    db.add(user)
    db.commit()

    payload = {
        "email": "duplicate@example.com",
        "username": "anotheruser",
        "password": "anotherpassword"
    }
    response = client.post("api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_register_existing_username(client, db):
    # Создаем пользователя с существующим username
    user = Users(id=uuid4(), email="uniqueemail@example.com", username="duplicateuser", hashed_password="hashed_pwd")
    db.add(user)
    db.commit()

    payload = {
        "email": "anotheremail@example.com",
        "username": "duplicateuser",
        "password": "anotherpassword"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login_success(client, db):
    user = Users(
        id=uuid4(),
        email="login@example.com",
        username="loginuser",
        hashed_password=get_password_hash("password") 
    )
    db.add(user)
    db.commit()

    # Попытка входа с правильным паролем
    response = client.post("/api/v1/auth/login", data={"username": "loginuser", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_username(client, db):
    response = client.post("api/v1/auth/login", data={"username": "nonexistent", "password": "password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_login_wrong_password(client, db):
    # Создаем пользователя
    user = Users(
        id=uuid4(),
        email="wrongpwd@example.com",
        username="wrongpwduser",
        hashed_password="$2b$12$KIXs0yZ2GQG1zTpQJpGQ5u5nXlD1VdGdU0Q4KIgFktYD1f1yrdl2a"
    )
    db.add(user)
    db.commit()

    response = client.post("api/v1/auth/login", data={"username": "wrongpwduser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_read_users_me(client, db):
    from app.core.security import create_access_token
    user = Users(id=uuid4(), email="me@example.com", username="meuser", hashed_password="hashed_pwd")
    db.add(user)
    db.commit()

    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["username"] == "meuser"

def test_logout(client, db):
    from app.core.security import create_access_token
    user = Users(id=uuid4(), email="logout@example.com", username="logoutuser", hashed_password="hashed_pwd")
    db.add(user)
    db.commit()

    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("api/v1/auth/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

def test_logout_invalid_token(client):
    headers = {"Authorization": "Bearer invalidtoken"}

    response = client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials" 
