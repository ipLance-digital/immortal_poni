from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from uuid import UUID
from app.models.users import Users
from app.schemas.users import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserList,
)
from typing import Dict
from app.api.base import BaseApi


class UsersApi(BaseApi):
    def __init__(self):
        super().__init__()
        self.router.add_api_route(
            "", self.get_users, methods=["GET"], response_model=UserList
        )
        self.router.add_api_route(
            "",
            self.create_user,
            methods=["POST"],
            response_model=UserResponse,
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            "/{user_id}", self.get_user, methods=["GET"], response_model=UserResponse
        )
        self.router.add_api_route(
            "/change_data",
            self.update_user,
            methods=["PATCH"],
            response_model=UserResponse,
        )

    def check_superuser(self, user: Users):
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail="Forbidden")

    async def get_users(
        self,
        skip: int = 0,
        limit: int = 10,
        current_user: Users = Depends(BaseApi.get_current_user),
    ):
        """
        Получение списка пользователей с пагинацией.
        """
        self.check_superuser(current_user)

        async with self.db as db:
            result = await db.execute(select(Users).offset(skip).limit(limit))
            users = result.scalars().all()
            total_result = await db.execute(select(func.count()).select_from(Users))
            total = total_result.scalar()
        return {"total": total, "items": users}

    async def get_user(
        self,
        user_id: UUID,
        current_user: Users = Depends(BaseApi.get_current_user),
    ) -> UserResponse:
        """
        Получение данных конкретного пользователя.

        Args:
            current_user: Авторизованный пользователь
            user_id: UUID пользователя

        Returns:
            UserResponse: Данные пользователя

        Raises:
            HTTPException: Если пользователь не найден
        """
        async with self.db as db:
            user = await db.execute(select(Users).where(Users.id == user_id))
            user = user.scalars().first()
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
        return user

    async def create_user(
        self,
        user: UserCreate,
        current_user: Users = Depends(BaseApi.get_current_user),
    ) -> UserResponse:
        """
        Создание нового пользователя.
        """
        self.check_superuser(current_user)

        async with self.db as db:
            result = await db.execute(select(Users).where(Users.email == user.email))
            db_user = result.scalars().first()
            if db_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
            result = await db.execute(
                select(Users).where(Users.username == user.username)
            )
            db_user = result.scalars().first()
            if db_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered",
                )
            hashed_password = self.security.get_password_hash(user.password)
            db_user = Users(
                email=user.email,
                username=user.username,
                hashed_password=hashed_password,
            )
            db.add(db_user)
            await self.update_db(db, db_user)
        return db_user

    async def update_user(
        self,
        user: UserUpdate,
        current_user: Users = Depends(BaseApi.get_current_user),
    ) -> UserResponse:
        """
        Обновление данных пользователя.
        """
        async with self.db as db:
            db_user = current_user
            if db_user is None:
                raise HTTPException(status_code=404, detail="User not found")

            update_data: Dict = user.model_dump(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = self.security.get_password_hash(
                    update_data.pop("password")
                )

            for field, value in update_data.items():
                setattr(db_user, field, value)

            db.add(db_user)
            await self.update_db(db, db_user)
        return db_user
