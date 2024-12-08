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
            sorted_scores = [
                (float(score), int(attraction_id))
                for attraction_id, score in self.redis_client.zrevrange(redis_key, 0, -1, withscores=True)
            ]
        else:
            sorted_scores = self._compute_and_store_scores(user, redis_key)

        ordered_attractions_in_chunks = self._calculate_indices_to_return_attractions_in_chunks(sorted_scores, page,
                                                                                                page_size)
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
                    print(
                        f"Skipping attraction {attraction_id} due to dimension mismatch: "
                        f"user_embedding({user_embedding.shape[0]}) vs "
                        f"attraction_embedding({attraction_embedding.shape[0]})"
                    )
                    continue
                score = cosine_similarity([user_embedding], [attraction_embedding])[0][0]
                scores.append((score, attraction_id))

            sorted_scores = sorted(scores, key=lambda x: x[0], reverse=True)

            for score, attraction_id in sorted_scores:
                self.redis_client.zadd(redis_key, {attraction_id: float(score)})

            return sorted_scores
        else:
            return None

    def _calculate_indices_to_return_attractions_in_chunks(self, sorted_scores, page: int, page_size: int):
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        if sorted_scores:
            paginated_scores = sorted_scores[start_index:end_index]

            attraction_ids = [attraction_id for _, attraction_id in paginated_scores]
            attractions = self.db.query(TouristAttraction).filter(TouristAttraction.id.in_(attraction_ids)).all()

            id_to_attraction = {attraction.id: attraction for attraction in attractions}
            ordered_attractions = [id_to_attraction[attraction_id] for _, attraction_id in paginated_scores]

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
