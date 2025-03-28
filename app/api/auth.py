from typing import Annotated
from datetime import datetime, UTC
import os
from jose import JWTError, jwt
from sqlalchemy import func
from sqlalchemy.future import select
from fastapi import (
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from app.api.base import BaseApi
from app.core.logger import logger
from app.models.users import Users
from app.schemas.auth import LoginRequest
from app.schemas.users import (
    UserCreate,
    UserResponse,
)


class AuthApi(BaseApi):
    def __init__(self):
        super().__init__()
        self.tags = ["Authentication"]
        self.router.add_api_route(
            "/me",
            self.read_users_me,
            methods=["GET"],
            response_model=UserResponse,
        )
        self.router.add_api_route(
            "/register",
            self.register_user,
            methods=["POST"],
            response_model=UserResponse,
        )
        self.router.add_api_route(
            "/login",
            self.login,
            methods=["POST"],
        )
        self.router.add_api_route(
            "/logout",
            self.logout,
            methods=["POST"],
        )
        self.router.add_api_route(
            "/refresh",
            self.refresh_access_token,
            methods=["POST"],
        )

    async def read_users_me(
        self,
        current_user: Annotated[Users, Depends(BaseApi.get_current_user)],
    ):
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        return current_user

    async def register_user(self, user: UserCreate):
        async with self.db as db:
            result = await db.execute(
                select(Users).where(func.lower(Users.username) == user.username.lower())
            )
            db_user = result.scalars().first()
            if db_user:
                raise HTTPException(
                    status_code=400,
                    detail="Username already registered",
                )
            result = await db.execute(select(Users).where(Users.email == user.email))
            db_user = result.scalars().first()
            if db_user:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered",
                )
            result = await db.execute(select(Users).where(Users.phone == user.phone))
            db_user = result.scalars().first()
            if db_user:
                raise HTTPException(
                    status_code=400,
                    detail="Phone already registered",
                )
            hashed_password = self.security.get_password_hash(user.password)
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

    async def login(self, login_data: LoginRequest, response: Response):
        async with self.db as db:
            if login_data.username:
                result = await db.execute(
                    select(Users).where(
                        func.lower(Users.username) == login_data.username.lower()
                    )
                )
            elif login_data.email:
                result = await db.execute(
                    select(Users).where(
                        func.lower(Users.email) == login_data.email.lower()
                    )
                )
            else:
                result = await db.execute(
                    select(Users).where(Users.phone == login_data.phone)
                )
            user = result.scalars().first()
            if not user or not self.security.verify_password(
                login_data.password, user.hashed_password
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                )
            await self.security.create_and_store_tokens(
                {"sub": user.username}, response
            )
            return UserResponse.model_validate(user.__dict__)

    async def logout(
        self,
        request: Request,
        response: Response,
        current_user: Users = Depends(BaseApi.get_current_user),
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
                    await self.security.blacklist_token(token, expires)
                    response.delete_cookie("access_token")
                    return {"message": "Successfully logged out"}
        except JWTError:
            logger.warning(f"Invalid token for user {current_user.username}")
        raise HTTPException(status_code=400, detail="Invalid token")

    async def refresh_access_token(
        self,
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
        if await self.security.is_token_blacklisted(refresh_token):
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
        access_token = self.security.create_access_token(data={"sub": username})
        self.security.set_token_cookie(
            response, access_token, refresh_token, csrf_token
        )
        return f"Create access tocken for {username}"
