from fastapi import FastAPI

from app.api.routes import users, projects, auth

app = FastAPI(title="Freelance Platform API", version="1.0.0")

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "Welcome to the Freelance Platform API"}
