import json
from sqlalchemy.orm import Session
from app.models.user_interaction import UserInteraction
from datetime import datetime

class InteractionsMatrixHelper:
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis_client = redis_client
        self.redis_key = 'user_interactions_matrix'


    async def create_user_interactions_matrix(self, data=None):
        redis_data = {}

        interactions = data if data is not None else self.db.query(UserInteraction).all()
        for interaction in interactions:
            redis_data[f"{interaction.user_id},{interaction.attraction_id}"] = interaction.rating

        await self.redis_client.set(self.redis_key, json.dumps(redis_data))


    async def update_user_interactions_matrix(self, user_id: int, attraction_id: int, rating: int):
        if not await self.redis_client.exists(self.redis_key):
            await self.create_user_interactions_matrix()
        else:
            redis_data = await self.redis_client.get(self.redis_key)
            matrix = json.loads(redis_data)
            matrix[f"{user_id},{attraction_id}"] = rating
            await self.redis_client.set(self.redis_key, json.dumps(matrix))







