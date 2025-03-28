import os

from fastapi import APIRouter, Request, HTTPException, status
from uuid import UUID

from app.core.database import PgSingleton
from app.core.security import Security
from app.core.storage import SupabaseStorage
from app.models.users import Users
from sqlalchemy import select
from jose import JWTError, jwt


class BaseApi:
    security = Security()
    storage = SupabaseStorage()
    debug = os.getenv("DEBUG", "False")
    db_connection = PgSingleton()
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BaseApi, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.prefix = f"/{self.__class__.__name__.split('Api')[0].lower()}"
        self.tags = [self.__class__.__name__.split("Api")[0]]
        self.router = APIRouter()

    @property
    def db(self):
        return self.db_connection.session

    async def update_db(self, context, update_obj=None):
        await context.commit()
        if update_obj:
            await context.refresh(update_obj)

    async def user_exists(self, db_session, user_id: UUID) -> bool:
        """
        Проверка на наличие пользователя в бд.
        """
        result = await db_session.execute(select(Users).filter(Users.id == user_id))
        user = result.scalar_one_or_none()
        return user

    @classmethod
    async def get_current_user(cls, request: Request) -> Users:
        if cls.debug.lower() in ("true", "1", "t", "y", "yes"):
            async with cls.db_connection.session as db:
                user = await db.execute(
                    select(Users).where(Users.username == "superuser")
                )
                user = user.scalars().first()
                if user is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Could not validate credentials",
                    )
                return user
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        csrf_token = request.cookies.get("csrf_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing"
            )
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
            )
        if not csrf_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="CSRF token missing"
            )
        if csrf_token != request.headers.get("X-CSRF-TOKEN"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid CSRF token"
            )
        if await cls.security.is_token_blacklisted(access_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token has been revoked",
            )
        if await cls.security.is_token_blacklisted(refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
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
                    detail="Could not validate credentials",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        async with PgSingleton().session as db:
            user = await db.execute(
                select(Users).where(Users.username.ilike(username.lower()))
            )
            user = user.scalars().first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
            return user
