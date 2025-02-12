"""
Модуль управления пользователями.
Содержит CRUD операции для работы с пользователями.
"""
from typing import Annotated, Dict, List, Type
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.users import Users
from app.schemas.users import UserCreate, UserUpdate, UserResponse, UserList
from app.core.security import get_password_hash
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("", response_model=UserList)
async def get_users(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db),
) -> dict[str, list[Type[Users]] | int]:
    """
    Получение списка пользователей с пагинацией.

    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей
        db: Сессия базы данных

    Returns:
        UserList: Список пользователей и общее количество
    """
    users = db.query(Users).offset(skip).limit(limit).all()
    total = db.query(Users).count()
    return {"total": total, "items": users}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: UUID,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
) -> UserResponse:
    """
    Получение данных конкретного пользователя.

    Args:
        user_id: UUID пользователя
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь

    Returns:
        UserResponse: Данные пользователя

    Raises:
        HTTPException: Если пользователь не найден
    """

    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
async def create_user(
        user: UserCreate,
        db: Session = Depends(get_db),
) -> Users:
    """
    Создание нового пользователя.

    Args:
        user: Данные для создания пользователя
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь

    Returns:
        UserResponse: Данные созданного пользователя

    Raises:
        HTTPException: Если email или username уже заняты
    """
    db_user = db.query(Users).filter(Users.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = db.query(Users).filter(Users.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400,
                            detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    db_user = Users(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: UUID,
        user: UserUpdate,
        db: Session = Depends(get_db),
        current_user: Users = Depends(get_current_user)
) -> UserResponse:
    """
    Обновление данных пользователя.

    Args:
        user_id: UUID пользователя
        user: Данные для обновления
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь

    Returns:
        UserResponse: Обновленные данные пользователя

    Raises:
        HTTPException: Если пользователь не найден
    """
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(
            update_data.pop("password"))

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user
