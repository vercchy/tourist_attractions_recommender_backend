from fastapi import APIRouter

authentication_router = APIRouter(
    prefix="/api/authentication",
    tags=["authentication"],
)

from app.api.authentication import register
from app.api.authentication import login

router = authentication_router