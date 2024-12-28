from fastapi.openapi.utils import status_code_ranges

from app.service.attractions.attraction_service import AttractionService
from app.api.routers.attractions_router import attractions_router
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.session import get_db
from app.utils.utils import decode_access_token


@attractions_router.get('/{attraction_id}')
async def get_attraction(attraction_id: int, db: Session = Depends(get_db)):
    attraction_service = AttractionService(db)
    return attraction_service.get_attraction(attraction_id)

@attractions_router.post('/rate/{attraction_id}')
async def rate_attraction(
        attraction_id: int,
        rating: int,
        db: Session = Depends(get_db),
        payload=Depends(decode_access_token)):
    user = payload.get('sub')
    if user is None:
        raise HTTPException(status_code=400, detail='Unauthorized')
    attraction_service = AttractionService(db)
    return attraction_service.rate_attraction(attraction_id, user, rating)


