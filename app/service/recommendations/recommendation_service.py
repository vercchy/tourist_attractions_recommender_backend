from app.service.recommendations.base_service import BaseRecommendationService
from app.models.user import User
from fastapi import HTTPException
from app.schemas.attractions_schema import TouristAttractionResponse


class RecommendationService(BaseRecommendationService):
    def recommend(self, user_id: int, page: int, page_size: int):
        redis_key = f"user:{user_id}"
        if self.redis_client.exists(redis_key):
            sorted_attractions_ids = self.retrieve_sorted_ids_from_cache(redis_key)
        else:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=400, detail="User not found")

            keys = self.redis_client.keys("attraction:*")
            attraction_ids = (int(key.split(b":")[1]) for key in keys)
            sorted_attractions_ids = self.calculate_similarity_scores(user, attraction_ids)
            self.cache_sorted_ids(sorted_attractions_ids, redis_key, 86400)

        ordered_attractions_in_chunks = (self.calculate_indices_to_return_attractions_in_chunks
                                         (sorted_attractions_ids, page, page_size))
        return [TouristAttractionResponse.model_validate(attraction) for attraction in ordered_attractions_in_chunks]
