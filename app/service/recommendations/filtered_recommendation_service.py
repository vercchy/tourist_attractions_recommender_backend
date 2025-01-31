from fastapi import HTTPException
from app.models.user import User
from app.models.tourist_attraction import TouristAttraction
from app.schemas.attractions_schema import TouristAttractionResponse
from app.service.recommendations.base_service import BaseRecommendationService


class FilteredRecommendationService(BaseRecommendationService):
    async def recommend(self, user_id: int, page: int, page_size: int, country_id: int, city_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        redis_key = f"user:{user_id}-{country_id}-{city_id or 'all'}"

        if await self.redis_client.exists(redis_key):
            sorted_attraction_ids = await self.retrieve_sorted_ids_from_cache(redis_key)
        else:
            query = self.db.query(TouristAttraction.id).filter(TouristAttraction.country_id == country_id)
            if city_id:
                query = query.filter(TouristAttraction.city_id == city_id)
            attraction_ids = [attraction_id for attraction_id, in query.all()]

            high_rating_attractions = await self.concat_prepared_embeddings_and_make_predictions(user_id,
                                                                                                 attraction_ids)
            sorted_attraction_ids = await self.calculate_similarity_scores(user, high_rating_attractions)

            await self.cache_sorted_ids(sorted_attraction_ids, redis_key, 1800)

        ordered_attractions_in_chunks = (await self.calculate_indices_to_return_attractions_in_chunks
                                             (sorted_attraction_ids, page, page_size))
        return [TouristAttractionResponse.model_validate(attraction) for attraction in ordered_attractions_in_chunks]
