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
from app.core.database import PgSingleton
from app.core.logger import logger
from app.core.security import (
    create_access_token,
    blacklist_token,
    get_password_hash,
    is_token_blacklisted,
    set_token_cookie,
    verify_password, create_refresh_token, create_csrf_token,
    create_and_store_tokens,
)
from app.models.users import Users
from app.schemas.auth import LoginRequest
from app.schemas.users import UserCreate, UserResponse

router = APIRouter()

async def get_current_user(request: Request) -> Users:
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    csrf_token = request.cookies.get("csrf_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing"
        )
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )
    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CSRF token missing"
        )
    if csrf_token != request.headers.get("X-CSRF-TOKEN"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid CSRF token"
        )
    if await is_token_blacklisted(access_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has been revoked"
        )
    if await is_token_blacklisted(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked"
        )
    try:
        payload = jwt.decode(
            access_token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")],
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    async with PgSingleton().session as db:
        user = await db.execute(
            select(Users).where(Users.username.ilike(username.lower()))
        )
        user = user.scalars().first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
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

@router.post("/login")
async def login(
        login_data: LoginRequest,
        response: Response
):
    async with PgSingleton().session as db:
        if login_data.username:
            result = await db.execute(
                select(Users).where(func.lower(Users.username) == func.lower(login_data.username))
            )
        elif login_data.email:
            result = await db.execute(
                select(Users).where(func.lower(Users.email) == func.lower(login_data.email))
            )
        else:
            result = await db.execute(
                select(Users).where(Users.phone == login_data.phone)
            )
        user = result.scalars().first()
        if not user or not verify_password(
                login_data.password,
                user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        await create_and_store_tokens({"sub": user.username}, response)
        return UserResponse.model_validate(user.__dict__)

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: Users = Depends(get_current_user),
):
    token = request.cookies.get("access_token")
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
    raise HTTPException(
        status_code=400,
        detail="Invalid token"
    )

@router.post("/refresh")
async def refresh_access_token(
        request: Request,
        response: Response,
):
    refresh_token = request.cookies.get("refresh_token")
    csrf_token = request.cookies.get("csrf_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CSRF token missing",
        )
    if await is_token_blacklisted(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )
    try:
        payload = jwt.decode(
            refresh_token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")],
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    access_token = create_access_token(data={"sub": username})
    set_token_cookie(
        response,
        access_token,
        refresh_token,
        csrf_token
    )
    return f"Create access tocken for {username}"
