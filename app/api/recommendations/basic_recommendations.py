from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.redis import get_redis_client
from app.api.recommendations import recommendations_router
from app.utils.auth import decode_access_token
from app.service.recommendations.recommendation_service import RecommendationService


@recommendations_router.get("")
async def get_recommendations(
        page: int = 1,
        page_size: int = 10,
        db: Session = Depends(get_db),
        redis_client=Depends(get_redis_client),
        payload=Depends(decode_access_token)):
    recommendation_service = RecommendationService(db, redis_client)
    user = payload.get("sub")
    recommendations = await recommendation_service.recommend(int(user), page, page_size)
    return recommendations


