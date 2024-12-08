from fastapi import APIRouter

cities_router = APIRouter(
    prefix="/api/cities",
    tags=["cities"],
)

from app.api.cities import cities