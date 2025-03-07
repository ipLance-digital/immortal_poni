import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from app.core.database import PgSingleton
from app.main import app
from app.models.files import Files
from app.models.users import Users


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


async def delete_user(username):
    async with PgSingleton().session as db:
        result = await db.execute(
            select(Users.id).where(Users.username == username))
        user_id = result.scalar()
        if user_id is None:
            return None
        await db.execute(delete(Files).where(Files.created_by == user_id))
        await db.commit()
        stmt_user = delete(Users).where(Users.id == user_id)
        await db.execute(stmt_user)
        await db.commit()
        await PgSingleton().close_connections()
