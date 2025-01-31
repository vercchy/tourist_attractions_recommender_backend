import json
from fastapi import HTTPException
from app.models.user import User
from app.models.user_interaction import UserInteraction
from app.schemas.attractions_schema import TouristAttractionResponse
from app.service.recommendations.base_service import BaseRecommendationService


class RecommendationService(BaseRecommendationService):

    async def recommend(self, user_id: int, page: int, page_size: int):
        redis_key = f"user:{user_id}"
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        if await self.redis_client.exists(redis_key):
            sorted_attraction_ids = await self.retrieve_sorted_ids_from_cache(redis_key)
        else:
            keys = await self.redis_client.keys("attraction:*")
            attraction_ids = [int(key.split(b":")[1]) for key in keys]

            rated_attractions = set(
                attraction_id[0] for attraction_id in
                self.db.query(UserInteraction.attraction_id).filter(UserInteraction.user_id == user_id).all()
            )
            unrated_attractions = [aid for aid in attraction_ids if aid not in rated_attractions]

            high_rating_attractions = await self.concat_prepared_embeddings_and_make_predictions(user_id, unrated_attractions)

            sorted_attraction_ids = await self.calculate_similarity_scores(user, high_rating_attractions)

            await self.cache_sorted_ids(sorted_attraction_ids, redis_key, 86400)

        ordered_attractions_in_chunks = (await self.calculate_indices_to_return_attractions_in_chunks
                                         (sorted_attraction_ids, page, page_size))
        return [TouristAttractionResponse.model_validate(attraction) for attraction in ordered_attractions_in_chunks]