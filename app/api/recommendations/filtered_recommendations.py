from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.redis import get_redis_client
from app.api.recommendations import recommendations_router
from app.utils.auth import decode_access_token
from app.service.recommendations.filtered_recommendation_service import FilteredRecommendationService


@recommendations_router.get("/filtered")
def get_filtered_recommendations(
        country_id: int,
        page: int = 1,
        page_size: int = 10,
        city_id: int = None,
        db: Session = Depends(get_db),
        redis_client=Depends(get_redis_client),
        payload=Depends(decode_access_token)):
    recommendation_service = FilteredRecommendationService(db, redis_client)
    user = payload.get("sub")
    return recommendation_service.recommend(int(user), page, page_size, country_id, city_id)