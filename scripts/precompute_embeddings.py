import pickle
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.tourist_attraction import TouristAttraction
from app.utils.redis import get_redis_client
from app.service.embedding import load_glove_model, compute_embedding



async def save_embeddings_to_file(database: Session, model, file_path = r"C:\Users\krist\Dev\tourist_attractions_recommender_backend\tourist_attractions_recommender_backend\scripts\embeddings.pkl"):
    embeddings = {}

    attractions = database.query(TouristAttraction).all()
    for attraction in attractions:
        text = attraction.description or attraction.comment or ''
        embedding = compute_embedding(text, model)
        embeddings[attraction.id] = embedding

    with open(file_path, "wb") as f:
        pickle.dump(embeddings, f)

    print(f"Embeddings saved locally to file {file_path}")


async def load_embeddings_from_file(file_path = r"C:\Users\krist\Dev\tourist_attractions_recommender_backend\tourist_attractions_recommender_backend\scripts\embeddings.pkl"):
    with open(file_path, "rb") as f:
        embeddings = pickle.load(f)
    print(f"Loaded embeddings from file {file_path}")
    return embeddings


async def populate_reddis_from_file(redis_client, file_path = r"C:\Users\krist\Dev\tourist_attractions_recommender_backend\tourist_attractions_recommender_backend\scripts\embeddings.pkl"):
    embeddings = await load_embeddings_from_file(file_path)
    for attraction_id, embedding in embeddings.items():
        await redis_client.set(f"attraction:{attraction_id}", embedding.tobytes())
        print(f"Added attraction with id {attraction_id} to redis cache")

    print("Redis cache populated from file.")



