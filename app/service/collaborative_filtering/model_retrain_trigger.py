import re
from fastapi import BackgroundTasks
import json
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
from app.models.user import User
from app.models.user_interaction import UserInteraction
from app.models.tourist_attraction import TouristAttraction
from datetime import datetime
from app.service.collaborative_filtering.model_retrainer import gather_data_and_trigger_retraining

async def train_and_cache_collaborative_model(db, redis_client):
    max_user_id = db.query(UserInteraction.user_id).order_by(UserInteraction.user_id.desc()).first()[0] or 0
    max_attraction_id = db.query(UserInteraction.attraction_id).order_by(UserInteraction.attraction_id.desc()).first()[0] or 0

    redis_key = "user_interactions_matrix"
    if not await redis_client.get(redis_key):
        raise ValueError("Sparse matrix not found in redis")

    redis_data = await redis_client.get(redis_key)
    data = json.loads(redis_data)

    matrix_csr = await create_sparse_matrix(data, max_user_id, max_attraction_id)

    predicted_ratings = await make_predictions(matrix_csr)

    valid_attraction_ids = {
        attraction.id for attraction in db.query(TouristAttraction.id).all()
    }

    for user_id in range(1, max_user_id + 1):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user_predictions = {
                str(attraction_id): float(predicted_ratings[user_id, attraction_id])
                for attraction_id in valid_attraction_ids
                if attraction_id < predicted_ratings.shape[1]
            }
            await redis_client.set(f"user:{user_id}:predictions", json.dumps(user_predictions))

    await redis_client.set("collaborative_model_last_trained", datetime.utcnow().isoformat())

    await clear_user_predictions_after_gathering_new_data(redis_client)
    await redis_client.delete("model_currently_trained")

    print("Collaborative filtering model trained and predictions cached")


async def create_sparse_matrix(data, num_users, num_attractions):
    rows, columns, values = [], [], []

    for key, value in data.items():
        user_id, attraction_id = map(int, key.split(","))
        rows.append(user_id)
        columns.append(attraction_id)
        values.append(value)

    return csr_matrix((values, (rows, columns)), shape=(num_users + 1, num_attractions + 1), dtype=np.float32)


async def make_predictions(matrix_csr):
    k = max(10, min(100, min(matrix_csr.shape[0], matrix_csr.shape[1]) // 10))

    u, sigma, vt = svds(matrix_csr, k=k)
    sigma = np.diag(sigma)

    return np.dot(np.dot(u, sigma), vt)


async def clear_user_predictions_after_gathering_new_data(redis_client):
    print("Clearing user predictions..")
    cursor = "0"
    pattern = "user:[0-9]*"

    while cursor != 0:
        cursor, keys = await redis_client.scan(cursor=cursor, match=pattern, count=100)
        valid_keys = [key for key in keys if re.match(r"user:\d+$", key.decode("utf-8"))]
        if valid_keys:
            await redis_client.delete(*valid_keys)

    print("User predictions cleared")


async def prepare_to_trigger_training(db, redis_client, background_tasks: BackgroundTasks):
    if await redis_client.exists("model_currently_trained"):
        print("One background task had already been triggered")
        return
    await trigger_model_training_if_needed(db, redis_client, background_tasks)



async def trigger_model_training_if_needed(db, redis_client, background_tasks: BackgroundTasks, change_threshold: float = 0.05):
    total_interactions = db.query(UserInteraction).count()
    changes_count = await count_changes_since_last_training_of_model(db, redis_client)
    #change_ratio = changes_count / total_interactions if total_interactions > 0 else 0

    #if change_ratio > change_threshold:
        #print("Triggering model training...")
        #background_tasks.add_task(gather_data_and_trigger_retraining, db, redis_client)
    if changes_count >= 1:
        print("Triggering model training...")
        await redis_client.set("model_currently_trained", "true")
        background_tasks.add_task(gather_data_and_trigger_retraining, db, redis_client)
    else:
        print("Not enough changes since last model training")


async def count_changes_since_last_training_of_model(db, redis_client):
    last_training_time = await redis_client.get("collaborative_model_last_trained")
    if last_training_time is not None:
        last_training_time = datetime.fromisoformat(last_training_time.decode())
    else:
        last_training_time = datetime.min

    change_count = db.query(UserInteraction).filter(UserInteraction.last_updated > last_training_time).count()
    return change_count





