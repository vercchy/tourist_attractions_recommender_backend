import json
import numpy as np
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity
from app.models.tourist_attraction import TouristAttraction


class BaseRecommendationService:
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis_client = redis_client

    async def calculate_similarity_scores(self, user, attraction_ids):
        user_embedding = np.frombuffer(user.embedding, dtype=np.float32)

        if len(attraction_ids) == 1:
            return await self.calculate_single_similarity_score(user_embedding, attraction_ids[0])

        scores = []

        for attraction_id in attraction_ids:
            score = await self.calculate_single_similarity_score(user_embedding, attraction_id)
            if score and score >= 0.85:
                scores.append((score, attraction_id))

        sorted_attraction_ids = [attraction_id for _, attraction_id in
                                 sorted(scores, key=lambda x: x[0], reverse=True)][:1000]
        return sorted_attraction_ids

    async def calculate_single_similarity_score(self, user_embedding, attraction_id):
        redis_key = f"attraction:{attraction_id}"
        embedding_bytes = await self.redis_client.get(redis_key)
        if not embedding_bytes:
            return None
        attraction_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
        if attraction_embedding.shape[0] != user_embedding.shape[0]:
            return None
        return cosine_similarity([user_embedding], [attraction_embedding])[0][0]


    async def cache_sorted_ids(self, sorted_ids, redis_key, expiry_time):
        await self.redis_client.set(redis_key, json.dumps(sorted_ids), ex=expiry_time)

    async def retrieve_sorted_ids_from_cache(self, redis_key):
        sorted_attraction_ids_by_user = await self.redis_client.get(redis_key)
        if not sorted_attraction_ids_by_user:
            return []
        return json.loads(sorted_attraction_ids_by_user)

    async def calculate_indices_to_return_attractions_in_chunks(self, sorted_attractions_ids, page: int, page_size: int):
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        if start_index >= len(sorted_attractions_ids):
            return []

        paginated_ids = sorted_attractions_ids[start_index:end_index]
        attractions = self.db.query(TouristAttraction).filter(TouristAttraction.id.in_(paginated_ids)).all()
        id_to_attraction = {attraction.id: attraction for attraction in attractions}
        return [id_to_attraction[attraction_id] for attraction_id in paginated_ids]

    async def obtain_collab_based_predictions_and_sort_in_order(self, user, content_based_sorted_attraction_ids, collab_weight: float = 0.6, content_weight: float = 0.4):
        user_predictions_key = f"user:{user.id}:predictions"

        if not await self.redis_client.exists(user_predictions_key):
            return None

        user_predictions_data = await self.redis_client.get(user_predictions_key)
        user_predictions = json.loads(user_predictions_data)

        collab_scores = [user_predictions.get(str(attraction_id), 0) for attraction_id in content_based_sorted_attraction_ids]

        if not collab_scores:
            return None

        collab_scores = self.normalize_collab_scores(collab_scores)

        combined_scores = []
        for attraction_id, collab_score in zip(content_based_sorted_attraction_ids, collab_scores):
            content_score = await self.calculate_similarity_scores(user, [attraction_id])

            weighted_collab_score = collab_score * collab_weight if content_score != 0 else collab_score
            weighted_content_score = content_score * content_weight if collab_score != 0 else content_score
            combined_score = weighted_collab_score + weighted_content_score

            combined_scores.append((combined_score, attraction_id))

        return [attraction_id for _, attraction_id in sorted(combined_scores, key=lambda x: x[0], reverse=True)]



    @staticmethod
    def normalize_collab_scores(scores):
            min_score = min(scores)
            max_score = max(scores)
            return [(score - min_score) / (max_score - min_score) for score in scores]
