from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.tourist_attraction import TouristAttraction
from app.models.user_interaction import UserInteraction
from app.service.recommendations.initial_implementation_user_interaction_matrix import InteractionsMatrixHelper

class AttractionService:

    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis_client = redis_client

    def get_attraction(self, attraction_id: int):
        return self.db.query(TouristAttraction).filter(TouristAttraction.id == attraction_id).first()

    async def rate_attraction(self, attraction_id: int, user_id: int, rating:int):
        attraction = self.get_attraction(attraction_id)
        if attraction is None:
            raise HTTPException(status_code=400, detail='Attraction not found')
        if not (1 <= rating <= 5):
            raise HTTPException(status_code=400, detail='Rating must be between 1 and 5')

        interaction = (
            self.db.query(UserInteraction)
            .filter_by(user_id=user_id, attraction_id=attraction_id)
            .first()
        )

        if interaction:
            interaction.rating = rating
        else:
            new_interaction = UserInteraction(user_id=user_id, attraction_id=attraction_id, rating=rating)
            self.db.add(new_interaction)

        self.db.commit()
        interactions_matrix_helper = InteractionsMatrixHelper(self.db, self.redis_client)
        await interactions_matrix_helper.update_user_interactions_matrix(user_id, attraction_id, rating)
