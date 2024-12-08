from app.api.routers.countries_router import countries_router
from app.service.countries.country_service import CountryService
from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi import Depends


@countries_router.get("")
async def get_countries(db: Session = Depends(get_db)):
    service = CountryService(db)
    countries = service.get_all_countries()
    return countries


@countries_router.get("/{country_id}/cities")
async def get_cities_in_country(country_id: int, db: Session = Depends(get_db)):
    service = CountryService(db)
    cities_in_country = service.get_all_cities_in_country(country_id)
    return cities_in_country
