from fastapi import APIRouter
from app.api.routes import users, auth


def get_router() -> APIRouter:
    router = APIRouter()

    router.include_router(
        auth.router,
        prefix="/auth",
        tags=["Authentication"]
    )

    router.include_router(
        users.router,
        prefix="/users",
        tags=["Users"]
    )

    return router
