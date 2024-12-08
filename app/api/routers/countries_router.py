from fastapi import APIRouter

countries_router = APIRouter(
    prefix="/api/countries",
    tags=["countries"],
)

from app.api.countries import countries