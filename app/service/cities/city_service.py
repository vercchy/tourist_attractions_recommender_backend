from sqlalchemy.orm import Session
from app.models.city import City


class CityService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_cities(self):
        return self.db.query(City).all()
