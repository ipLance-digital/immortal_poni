from typing import Annotated
from datetime import datetime, UTC

import os
from jose import JWTError, jwt
from sqlalchemy import func
from sqlalchemy.future import select
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from app.core.database import PgSingleton
from app.core.logger import logger
from app.core.security import (
    create_access_token,
    blacklist_token,
    get_password_hash,
    is_token_blacklisted,
    set_token_cookie,
    verify_password,
)
from app.models.users import Users
from app.schemas.auth import Token
from app.schemas.users import UserCreate, UserResponse


router = APIRouter()


async def get_current_user(request: Request) -> Users:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if await is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")],
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
        user = await db.execute(
            select(Users).where(Users.username.ilike(username))
        )
        user = user.scalars().first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[Users, Depends(get_current_user)],
):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    return current_user


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    async with PgSingleton().session as db:
        result = await db.execute(
            select(Users).where(Users.username == user.username)
        )
        db_user = result.scalars().first()
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Username already registered",
            )

        result = await db.execute(
            select(Users).where(Users.email == user.email)
        )
        db_user = result.scalars().first()
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )

        result = await db.execute(
            select(Users).where(Users.phone == user.phone)
        )
        db_user = result.scalars().first()
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Phone already registered",
            )

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
    response: Response = None,
):
    async with PgSingleton().session as db:
        result = await db.execute(
            select(Users).where(
                func.lower(Users.username) == func.lower(form_data.username)
            )
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": user.username})
        set_token_cookie(response, access_token)
        return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: Users = Depends(get_current_user),
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=400, detail="No token found")

    try:
        payload = jwt.decode(
            token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")],
        )
        exp = payload.get("exp")
        if exp:
            expires = int(exp - datetime.now(UTC).timestamp())
            if expires > 0:
                await blacklist_token(token, expires)
                response.delete_cookie("access_token")
                return {"message": "Successfully logged out"}
    except JWTError:
        logger.warning(f"Invalid token for user {current_user.username}")

    raise HTTPException(status_code=400, detail="Invalid token")
