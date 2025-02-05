from fastapi import FastAPI
import uvicorn
import os
# from api.routes import users, projects, auth
from api.routes import auth

app = FastAPI(title="Freelance Platform API", version="1.0.0")

# app.include_router(users.router, prefix="/users", tags=["Users"])
# app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "Welcome to the Freelance Platform API"}

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("LOCALHOST"), port=os.getenv("PORT"))
