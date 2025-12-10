from fastapi import APIRouter

from app.api.v1 import address

app_router = APIRouter(prefix="/api")

app_router.include_router(router=address.router)
