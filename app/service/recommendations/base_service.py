import json
import numpy as np
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity
from app.models.tourist_attraction import TouristAttraction


class BaseRecommendationService:
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis_client = redis_client

    def calculate_similarity_scores(self, user, attraction_ids):
        user_embedding = np.frombuffer(user.embedding, dtype=np.float32)

        scores = []

        for attraction_id in attraction_ids:
            redis_key = f"attraction:{attraction_id}"
            embedding_bytes = self.redis_client.get(redis_key)
            if not embedding_bytes:
                continue
            attraction_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            if attraction_embedding.shape[0] != user_embedding.shape[0]:
                continue
            score = cosine_similarity([user_embedding], [attraction_embedding])[0][0]
            if score >= 0.85:
                scores.append((score, attraction_id))

        sorted_attraction_ids = [attraction_id for _, attraction_id in
                                 sorted(scores, key=lambda x: x[0], reverse=True)][:1000]
        return sorted_attraction_ids

    def cache_sorted_ids(self, sorted_ids, redis_key, expiry_time):
        self.redis_client.set(redis_key, json.dumps(sorted_ids), ex=expiry_time)

    def retrieve_sorted_ids_from_cache(self, redis_key):
        return json.loads(self.redis_client.get(redis_key))

    def calculate_indices_to_return_attractions_in_chunks(self, sorted_attractions_ids, page: int, page_size: int):
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        if start_index >= len(sorted_attractions_ids):
            return []

        paginated_ids = sorted_attractions_ids[start_index:end_index]
        attractions = self.db.query(TouristAttraction).filter(TouristAttraction.id.in_(paginated_ids)).all()
        id_to_attraction = {attraction.id: attraction for attraction in attractions}
        return [id_to_attraction[attraction_id] for attraction_id in paginated_ids]
