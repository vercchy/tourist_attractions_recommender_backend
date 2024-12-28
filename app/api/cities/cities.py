from app.api.routers.cities_router import cities_router
from app.service.cities.city_service import CityService
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi import Depends


@cities_router.get("")
async def get_cities(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    city_service = CityService(db)
    return city_service.get_all_cities()

@cities_router.get("/{city_id}")
async def get_city(city_id: int, db: Session = Depends(get_db)):
    city_service = CityService(db)
    return city_service.get_city(city_id)


