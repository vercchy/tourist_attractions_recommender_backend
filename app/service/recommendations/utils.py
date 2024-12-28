import numpy as np
from sqlalchemy.orm import Session
from scipy.sparse import dok_matrix
from app.models.user_interaction import UserInteraction
import json

class RecommendationsHelper:
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis_client = redis_client
        self.redis_key = 'user_interactions_matrix'


    def create_user_interactions_matrix(self):
        max_user_id = self.db.query(UserInteraction.user_id).order_by(UserInteraction.user_id.desc()).first()[0] or 0
        max_attraction_id = self.db.query(UserInteraction.attraction_id).order_by(UserInteraction.attraction_id.desc()).first()[0] or 0

        matrix = dok_matrix((max_user_id, max_attraction_id), dtype=np.int32)

        interactions = self.db.query(UserInteraction).all()

        for interaction in interactions:
            user_index = interaction.user_id - 1
            attraction_index = interaction.attraction_id - 1
            matrix[user_index, attraction_index] = interaction.rating

        redis_data = {
            f"{user_index},{attraction_index}": int(rating)
            for (user_index, attraction_index), rating in matrix.items()
        }

        self.redis_client.set(self.redis_key, json.dumps(redis_data))
        return matrix

