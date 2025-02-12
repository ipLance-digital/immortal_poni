"""
Модуль аутентификации и авторизации.
Содержит эндпоинты для регистрации, входа и управления токенами.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
from datetime import datetime

from app.models.users import Users
from app.schemas.users import UserCreate, UserResponse
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    blacklist_token,
    is_token_blacklisted,
)
from app.database import get_db
from app.schemas.auth import Token
from app.core.logger import logger


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
) -> Users:
    """
    Получение текущего пользователя из JWT токена.

    Args:
        token: JWT токен из заголовка Authorization
        db: Сессия базы данных

    Returns:
        User: Объект пользователя

    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Users).filter(Users.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.

    Args:
        user: Данные нового пользователя
        db: Сессия базы данных

    Returns:
        UserResponse: Данные созданного пользователя

    Raises:
        HTTPException: Если email или username уже заняты
    """
    db_user = db.query(Users).filter(Users.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = db.query(Users).filter(Users.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = Users(
        email=user.email, username=user.username, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    Авторизация пользователя.

    - **username**: имя пользователя
    - **password**: пароль

    Returns:
        JWT токен для авторизации
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    user = (
        db.query(Users)
        .filter(func.lower(Users.username) == func.lower(form_data.username))
        .first()
    )

    if not user:
        logger.warning(f"Failed login attempt: user {form_data.username} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(
            f"Failed login attempt: incorrect password for user {form_data.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Successful login for user: {form_data.username}")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[Users, Depends(get_current_user)]):
    """
    Получение данных текущего пользователя.

    Returns:
        Данные авторизованного пользователя
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: Annotated[Users, Depends(get_current_user)],
    token: str = Depends(oauth2_scheme),
):
    """
    Выход из системы.

    Добавляет текущий токен в черный список.

    Returns:
        Сообщение об успешном выходе
    """
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        exp = payload.get("exp")
        if exp:
            expires = exp - int(datetime.utcnow().timestamp())
            if expires > 0:
                blacklist_token(token, expires)
                logger.info(f"User {current_user.username} logged out successfully")
                return {"message": "Successfully logged out"}
    except JWTError:
        pass

    raise HTTPException(status_code=400, detail="Invalid token")
