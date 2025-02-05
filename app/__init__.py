from fastapi import FastAPI

from app.routers import example_router  # Замените на реальные роутеры

app = FastAPI(title="Freelance Platform API", version="1.0.0")

app.include_router(example_router.router, prefix="/example", tags=["Example"])

@app.get("/")
def root():
    return {"message": "Welcome to the Freelance Platform API"}
