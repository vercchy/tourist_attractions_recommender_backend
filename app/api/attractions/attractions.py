from fastapi import Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.redis import get_redis_client
from app.api.attractions import attractions_router
from app.utils.auth import decode_access_token
from app.service.attractions.attraction_service import AttractionService
from app.service.collaborative_filtering.model_retrain_trigger import prepare_to_trigger_training


@attractions_router.get('/{attraction_id}')
async def get_attraction(attraction_id: int, db: Session = Depends(get_db), redis_client = Depends(get_redis_client)):
    attraction_service = AttractionService(db, redis_client)
    return attraction_service.get_attraction(attraction_id)


@attractions_router.post('/rate/{attraction_id}')
async def rate_attraction(
        attraction_id: int,
        rating: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        redis_client=Depends(get_redis_client),
        payload=Depends(decode_access_token)):
    user = payload.get('sub')
    if user is None:
        raise HTTPException(status_code=400, detail='Unauthorized')
    attraction_service = AttractionService(db, redis_client)
    await attraction_service.rate_attraction(attraction_id, int(user), rating)
    await prepare_to_trigger_training(db, redis_client, background_tasks)
    return {"message": "Rating submitted successfully"}


