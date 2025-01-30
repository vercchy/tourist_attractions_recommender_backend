from fastapi import BackgroundTasks
from app.models.user_interaction import UserInteraction
from datetime import datetime
from app.service.collaborative_filtering.model_retrainer import gather_data_and_trigger_retraining


async def prepare_to_trigger_training(db, redis_client, background_tasks: BackgroundTasks):
    if await redis_client.exists("model_currently_trained"):
        print("One background task had already been triggered")
        return
    await trigger_model_training_if_needed(db, redis_client, background_tasks)



async def trigger_model_training_if_needed(db, redis_client, background_tasks: BackgroundTasks, change_threshold: float = 0.05):
    total_interactions = db.query(UserInteraction).count()
    changes_count = await count_changes_since_last_training_of_model(db, redis_client)
    change_ratio = changes_count / total_interactions if total_interactions > 0 else 0

    if change_ratio > change_threshold:
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





