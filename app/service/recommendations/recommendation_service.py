import json

import numpy as np
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.tourist_attraction import TouristAttraction
from fastapi import HTTPException
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.attractions_schema import TouristAttractionResponse


class RecommendationService:
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis_client = redis_client

    def recommend(self, user_id: int, page: int, page_size: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        redis_key = f"user:{user_id}"

        if self.redis_client.exists(redis_key):
            sorted_attractions_ids = json.loads(self.redis_client.get(redis_key))
        else:
            sorted_attractions_ids = self._compute_and_store_scores(user, redis_key)

        ordered_attractions_in_chunks = (self._calculate_indices_to_return_attractions_in_chunks
                                         (sorted_attractions_ids, page, page_size))
        return [TouristAttractionResponse.model_validate(attraction) for attraction in ordered_attractions_in_chunks]

    def _compute_and_store_scores(self, user: User, redis_key: str):
        if user.embedding:
            user_embedding = np.frombuffer(user.embedding, dtype=np.float32)
            scores = []

            keys = self.redis_client.keys("attraction:*")
            for key in keys:
                attraction_id = int(key.split(b":")[1])
                embedding_bytes = self.redis_client.get(key)
                attraction_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                if attraction_embedding.shape[0] != user_embedding.shape[0]:
                    continue
                score = cosine_similarity([user_embedding], [attraction_embedding])[0][0]
                if score >= 0.85:
                    scores.append((score, attraction_id))

            sorted_attraction_ids = [attraction_id for _, attraction_id in sorted(scores, key=lambda x: x[0], reverse=True)][:1000]
            self.redis_client.set(redis_key, json.dumps(sorted_attraction_ids))
            self.redis_client.expire(redis_key, 86400)
            #expires after 24 hours

            return sorted_attraction_ids
        else:
            return None

    def _calculate_indices_to_return_attractions_in_chunks(self, sorted_attractions_ids, page: int, page_size: int):
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        if start_index >= len(sorted_attractions_ids):
            return []

        if sorted_attractions_ids:
            paginated_ids = sorted_attractions_ids[start_index:end_index]

            attractions = self.db.query(TouristAttraction).filter(TouristAttraction.id.in_(paginated_ids)).all()

            id_to_attraction = {attraction.id: attraction for attraction in attractions}
            ordered_attractions = [id_to_attraction[attraction_id] for attraction_id in paginated_ids]

            return ordered_attractions
        else:
            attractions = (
                self.db.query(TouristAttraction)
                .order_by(TouristAttraction.id)
                .offset(start_index)
                .limit(page_size)
                .all()
            )
            return attractions
