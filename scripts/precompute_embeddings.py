import pickle
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.tourist_attraction import TouristAttraction
from app.utils.redis import get_redis_client
from app.service.embedding import load_glove_model, compute_embedding


EMBEDDINGS_FILE = "embeddings.pkl"


def save_embeddings_to_file(database: Session, model, file_path=EMBEDDINGS_FILE):
    embeddings = {}

    attractions = database.query(TouristAttraction).all()
    for attraction in attractions:
        combined_text = (
            f"{attraction.description or ''} {attraction.comment or ''}".strip()
            if (attraction.description or '') != (attraction.comment or '')
            else attraction.description or ''
        )
        embedding = compute_embedding(combined_text, model)
        embeddings[attraction.id] = embedding

    with open(file_path, "wb") as f:
        pickle.dump(embeddings, f)

    print(f"Embeddings saved locally to file {file_path}")


def load_embeddings_from_file(file_path=EMBEDDINGS_FILE):
    with open(file_path, "rb") as f:
        embeddings = pickle.load(f)
    print(f"Loaded embeddings from file {file_path}")
    return embeddings


def populate_reddis_from_file(redis_client, file_path=EMBEDDINGS_FILE):
    embeddings = load_embeddings_from_file(file_path)
    for attraction_id, embedding in embeddings.items():
        redis_client.set(f"attraction:{attraction_id}", embedding.tobytes())
        print(f"Added attraction with id {id} to redis cache")

    print("Redis cache populated from file.")


if __name__ == "__main__":
    db = next(get_db())
    glove_model = load_glove_model()
    save_embeddings_to_file(db, glove_model)
    populate_reddis_from_file(get_redis_client())


