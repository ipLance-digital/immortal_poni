"""
Модуль аутентификации и авторизации.
Содержит эндпоинты для регистрации, входа и управления токенами.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import func
import os
from datetime import datetime
from app.models.users import Users
from app.schemas.users import (
    UserResponse, 
    UserCreate,
)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    blacklist_token,
    is_token_blacklisted,
)
from sqlalchemy.future import select
from app.schemas.auth import Token
from app.core.logger import logger
from app.database import PgSingleton

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> Users:
    """
    Получение текущего пользователя из JWT токена.
    """
    if await is_token_blacklisted(token): 
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with PgSingleton().session as db:
        user = await db.execute(select(Users).where(Users.username.ilike(username)))
        user = user.scalars().first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
):
    """
    Регистрация нового пользователя.
    """
    async with PgSingleton().session as db:
        result = await db.execute(select(Users).where(Users.username == user.username))
        db_user = result.scalars().first()
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        result = await db.execute(select(Users).where(Users.email == user.email))
        db_user = result.scalars().first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        result = await db.execute(select(Users).where(Users.phone == user.phone))
        db_user = result.scalars().first()
        if db_user:
            raise HTTPException(status_code=400, detail="Phone already registered")
        hashed_password = get_password_hash(user.password)
        db_user = Users(
            username=user.username,
            email=user.email,
            phone=user.phone,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Авторизация пользователя.
    """
    async with PgSingleton().session as db:
        result = await db.execute(
            select(Users).where(
                func.lower(Users.username) == func.lower(form_data.username)
            )
        )
        user = result.scalars().first()
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
    """
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User {current_user.username} requested their data.")
    return current_user

@router.post("/logout")
async def logout(
    current_user: Users = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):
    """
    Выход из системы.
    """
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        exp = payload.get("exp")
        if exp:
            expires = int(exp - datetime.utcnow().timestamp())
            if expires > 0:
                await blacklist_token(token, expires)  
                logger.info(f"User {current_user.username} logged out successfully")
                return {"message": "Successfully logged out"}
    except JWTError:
        logger.warning(f"Invalid token for user {current_user.username}")
    raise HTTPException(status_code=400, detail="Invalid token")
