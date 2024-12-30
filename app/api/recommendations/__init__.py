from fastapi import APIRouter

recommendations_router = APIRouter(
    prefix="/api/recommendations",
    tags=["recommendations"],
)

from app.api.recommendations import basic_recommendations
from app.api.recommendations import filtered_recommendations

router = recommendations_router