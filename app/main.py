from fastapi import FastAPI
import uvicorn
import os
from app.api.routes import users
from app.db.init_db import init_db


app = FastAPI(title="Freelance Platform API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Wellcome to IP-lance"}


@app.on_event("startup")
async def startup_event():
    init_db()


app.include_router(users.router, prefix="/users", tags=["users"])


if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("LOCALHOST"))

