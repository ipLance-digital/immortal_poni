from fastapi import FastAPI
import uvicorn
import os
from app.database import engine, Base
from app.routers import get_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Freelance Platform API", version="1.0.0")

router = get_router()
app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to IP-lance"}

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("LOCALHOST"), port=int(os.getenv("PORT")))


