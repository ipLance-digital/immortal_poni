from typing import List, Optional


#TODO убрать в модели
class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


#TODO сделать через базовый репозиторий
class UserRepository:
    def __init__(self, connection):
        self.connection = connection

    async def get_user(self, user_id: int) -> Optional[User]:
        row = await self.connection.fetchrow('SELECT id, name FROM users WHERE id = $1', user_id)
        if row:
            return User(id=row['id'], name=row['name'])
        return None

    async def add_user(self, user: User):
        await self.connection.execute('INSERT INTO users (id, name) VALUES ($1, $2)', user.id, user.name)

    async def get_all_users(self) -> List[User]:
        rows = await self.connection.fetch('SELECT id, name FROM users')
        return [User(id=row['id'], name=row['name']) for row in rows]


#TODO переименовать
class UnitOfWork:
    def __init__(self, connection):
        self.connection = connection
        self.user_repository = UserRepository(connection)

    async def __aenter__(self):
        await self.connection.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.connection.commit()
        else:
            await self.connection.rollback()
