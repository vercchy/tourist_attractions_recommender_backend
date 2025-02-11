from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.countries import countries_router
from app.service.countries.country_service import CountryService


@countries_router.get("")
async def get_countries(db: Session = Depends(get_db)):
    service = CountryService(db)
    return service.get_all_countries()


@countries_router.get("/{country_id}/cities")
async def get_cities_in_country(country_id: int, db: Session = Depends(get_db)):
    service = CountryService(db)
    return service.get_all_cities_in_country(country_id)


@countries_router.get("/{country_id}")
async def get_country(country_id: int, db: Session = Depends(get_db)):
    service = CountryService(db)
    return service.get_country(country_id)

