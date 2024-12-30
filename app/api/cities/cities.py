from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.cities import cities_router
from app.service.cities.city_service import CityService


@cities_router.get("")
async def get_cities(db: Session = Depends(get_db)):
    city_service = CityService(db)
    return city_service.get_all_cities()


@cities_router.get("/{city_id}")
async def get_city(city_id: int, db: Session = Depends(get_db)):
    city_service = CityService(db)
    return city_service.get_city(city_id)


