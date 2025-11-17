from fastapi import APIRouter

from api.v1 import user_routes, auth_routes

api_router = APIRouter()
api_router.include_router(auth_routes.router, prefix="/auth", tags=["authentication"])
api_router.include_router(user_routes.router, prefix="/users", tags=["users"])
