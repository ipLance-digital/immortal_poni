from fastapi import FastAPI
import uvicorn
import os
from app.api.routes import auth
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Freelance Platform API", version="1.0.0")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def root():
    return {"message": "Welcome to IP-lance"}

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("LOCALHOST"), port=int(os.getenv("PORT")))


