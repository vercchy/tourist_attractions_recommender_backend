from app.api.routers.recommendations_router import recommendations_router
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.redis import get_redis_client
from app.models.user import User
from app.utils.utils import decode_access_token
from app.service.recommendations.recommendation_service import RecommendationService


@recommendations_router.get("")
def get_recommendations(
        page: int = 1,
        page_size: int = 10,
        db: Session = Depends(get_db),
        redis_client=Depends(get_redis_client),
        payload=Depends(decode_access_token)):
    recommendation_service = RecommendationService(db, redis_client)
    user = payload.get("sub")
    return recommendation_service.recommend(int(user), page, page_size)


