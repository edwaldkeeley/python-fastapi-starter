from fastapi import APIRouter
from app.api.v1.routers import user_router

api_router = APIRouter()
api_router.include_router(user_router.router, prefix="/users", tags=["Users"])