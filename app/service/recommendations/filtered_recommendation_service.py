from fastapi import HTTPException
from app.models.user import User
from app.models.tourist_attraction import TouristAttraction
from app.schemas.attractions_schema import TouristAttractionResponse
from app.service.recommendations.base_service import BaseRecommendationService


class FilteredRecommendationService(BaseRecommendationService):
    def recommend(self, user_id: int, page: int, page_size: int, country_id: int, city_id: int):
        redis_key = f"user:{user_id}-{country_id}-{city_id or 'all'}"

        if self.redis_client.exists(redis_key):
            sorted_attraction_ids = self.retrieve_sorted_ids_from_cache(redis_key)
        else:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=400, detail="User not found")

            query = self.db.query(TouristAttraction.id).filter(TouristAttraction.country_id == country_id)
            if city_id:
                query = query.filter(TouristAttraction.city_id == city_id)
            attraction_ids = [attraction_id for attraction_id, in query.all()]

            sorted_attraction_ids = self.calculate_similarity_scores(user, attraction_ids)
            self.cache_sorted_ids(sorted_attraction_ids, redis_key, 1800)

        ordered_attractions_in_chunks = (self.calculate_indices_to_return_attractions_in_chunks
                                             (sorted_attraction_ids, page, page_size))
        return [TouristAttractionResponse.model_validate(attraction) for attraction in ordered_attractions_in_chunks]
