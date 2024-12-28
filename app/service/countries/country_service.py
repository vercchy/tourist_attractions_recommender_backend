from sqlalchemy.orm import Session
from app.models.country import Country


class CountryService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_countries(self):
        return self.db.query(Country).all()

    def get_all_cities_in_country(self, country_id: int):
        country = self.db.query(Country).filter(Country.id == country_id).first()
        if not country:
            return None
        return country.cities

    def get_country(self, country_id: int):
        return self.db.query(Country).filter(Country.id == country_id).first()

