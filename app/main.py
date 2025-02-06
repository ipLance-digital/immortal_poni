import asyncpg
from fastapi import FastAPI
import uvicorn
import os
from database.postgres import UnitOfWork, User


app = FastAPI(title="Freelance Platform API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Wellcome to IP-lance"}


@app.get("/create_user")
async def create_user():
    connection = await asyncpg.connect(user='postgres', password='postgres',
                                       database='test', host='127.0.0.1')
    async with UnitOfWork(connection) as uow:
        new_user = User(id=1, name='Alice')
        await uow.user_repository.add_user(new_user)


@app.get("/get_user")
async def get_user():
    connection = await asyncpg.connect(user='postgres', password='postgres',
                                       database='test', host='127.0.0.1')
    async with UnitOfWork(connection) as uow:
        user = await uow.user_repository.get_user(1)
    return {"user": user.name}


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("LOCALHOST"))

