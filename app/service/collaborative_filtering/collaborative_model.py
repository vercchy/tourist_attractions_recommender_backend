from fastapi import BackgroundTasks
import json
import numpy as np
from scipy.sparse import dok_matrix
from scipy.sparse.linalg import svds
from app.models.user import User
from app.models.user_interaction import UserInteraction
from app.service.recommendations.utils import InteractionsMatrixHelper
from datetime import datetime

async def train_and_cache_collaborative_model(db, redis_client):
    max_user_id = db.query(UserInteraction.user_id).order_by(UserInteraction.user_id.desc()).first()[0] or 0
    max_attraction_id = db.query(UserInteraction.attraction_id).order_by(UserInteraction.attraction_id.desc()).first()[0] or 0

    redis_key = "user_interactions_matrix"
    if not redis_client.get(redis_key):
        raise ValueError("Sparse matrix not found in redis")

    redis_data = await redis_client.get(redis_key)
    data = json.loads(redis_data)
    matrix = dok_matrix((max_user_id, max_attraction_id), dtype=np.float32)

    for key, value in data.items():
        user_index, attraction_index = map(int, key.split(","))
        matrix[user_index, attraction_index] = value

    matrix_csr = matrix.tocsr()
    k = max(1, min(10, min(matrix_csr.shape[0], matrix_csr.shape[1]) // 2))

    u, sigma, vt = svds(matrix_csr, k=k)
    sigma = np.diag(sigma)

    predicted_ratings = np.dot(np.dot(u, sigma), vt)
    for user_index in range(max_user_id):
        user = db.query(User).filter(User.id == user_index + 1).first()
        if user:
            user_predictions = {
                str(attraction_index): float(predicted_ratings[user_index, attraction_index])
                for attraction_index in range(max_attraction_id)
            }
            await redis_client.set(f"user:{user_index}:predictions", json.dumps(user_predictions))

    await redis_client.set("collaborative_model_last_trained", datetime.utcnow().isoformat())
    print("Collaborative filtering model trained and predictions cached")


async def trigger_model_training_if_needed(db, redis_client, background_tasks: BackgroundTasks, change_threshold: float = 0.05):
    total_interactions = db.query(UserInteraction).count()
    interactions_matrix_helper = InteractionsMatrixHelper(db, redis_client)
    changes_count = await interactions_matrix_helper.count_changes_since_last_training_of_model()
    #change_ratio = changes_count / total_interactions if total_interactions > 0 else 0

    #if change_ratio > change_threshold:
        #print("Triggering model training...")
        #background_tasks.add_task(train_and_cache_collaborative_model, db, redis_client)
    if changes_count >= 1:
        print("Triggering model training...")
        background_tasks.add_task(train_and_cache_collaborative_model, db, redis_client)
    else:
        print("Not enough changes since last model training")





