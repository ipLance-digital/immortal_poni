from fastapi import APIRouter
from uuid import UUID

from app.core.database import PgSingleton
from app.models.users import Users
from sqlalchemy import select


class BaseApi:
    def __init__(self):
        self.prefix = f"/{self.__class__.__name__.split('Api')[0].lower()}"
        self.tags = [self.__class__.__name__.split('Api')[0]]
        self.db_connection = PgSingleton()
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

