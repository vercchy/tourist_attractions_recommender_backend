from app.models import User
from app.service.embedding import compute_embedding

async def recalculate_user_embeddings(db, glove_model):
    users = db.query(User).all()
    for user in users:
        interests = user.description_of_interests
        new_embedding = compute_embedding(interests, glove_model).tobytes()
        user.embeddings = new_embedding
    db.commit()


