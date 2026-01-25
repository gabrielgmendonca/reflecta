from fastapi import APIRouter

from app.api.boards import router as boards_router
from app.api.templates import router as templates_router
from app.api.auth import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(boards_router, prefix="/boards", tags=["boards"])
api_router.include_router(templates_router, prefix="/templates", tags=["templates"])
