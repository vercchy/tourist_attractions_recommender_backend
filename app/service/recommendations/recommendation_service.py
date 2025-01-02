import json
from fastapi import HTTPException
from app.models.user import User
from app.schemas.attractions_schema import TouristAttractionResponse
from app.service.recommendations.base_service import BaseRecommendationService


class RecommendationService(BaseRecommendationService):
    async def recommend(self, user_id: int, page: int, page_size: int, collab_weight: float = 0.6, content_weight: float = 0.4):
        redis_key = f"user:{user_id}"
        user = self.db.query(User).filter(User.id == user_id).first()
        if await self.redis_client.exists(redis_key):
            sorted_attraction_ids = await self.retrieve_sorted_ids_from_cache(redis_key)
        else:
            if not user:
                raise HTTPException(status_code=400, detail="User not found")

            keys = await self.redis_client.keys("attraction:*")
            attraction_ids = [int(key.split(b":")[1]) for key in keys]
            sorted_attraction_ids = await self.calculate_similarity_scores(user, attraction_ids)

            sorted_attraction_ids = await self.obtain_collab_based_predictions_and_sort_in_order(user, sorted_attraction_ids) or sorted_attraction_ids
            await self.cache_sorted_ids(sorted_attraction_ids, redis_key, 86400)

        ordered_attractions_in_chunks = (await self.calculate_indices_to_return_attractions_in_chunks
                                         (sorted_attraction_ids, page, page_size))
        return [TouristAttractionResponse.model_validate(attraction) for attraction in ordered_attractions_in_chunks]
