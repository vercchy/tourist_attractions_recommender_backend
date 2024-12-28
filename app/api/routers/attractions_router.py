from fastapi import APIRouter

attractions_router = APIRouter(
    prefix="/api/attractions",
    tags=["attractions"],
)

from app.api.attractions import attractions