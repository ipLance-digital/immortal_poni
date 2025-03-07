import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from app.core.database import PgSingleton
from app.main import app
from app.models.files import Files
from app.models.orders import Order
from app.models.users import Users
from app.services.storage import SupabaseStorage


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


async def delete_user(username):
    """
        Удаление данных, оставшихся при тестировании эндпоинтов.
    """
    async with PgSingleton().session as db:
        result = await db.execute(
            select(Users.id).where(Users.username == username)
        )
        user_id = result.scalar()
        if user_id is None:
            return None
        # удаление тестовых ордеров
        await db.execute(
            delete(Order).where(Order.created_by == user_id)
        )
        # удаление тестовых файлов
        files_to_delete = await db.execute(
            select(Files.id).where(Files.created_by == user_id)
        )
        files_to_delete = files_to_delete.scalars().all()
        for file_uuid in files_to_delete:
            await SupabaseStorage.delete_file(file_uuid, user_id)
        await db.execute(
            delete(Files).where(Files.created_by == user_id)
        )
        # удаление тестового пользователя
        await db.execute(
            delete(Users).where(Users.id == user_id)
        )
        await db.commit()
        await PgSingleton().close_connections()
