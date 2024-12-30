from sqlalchemy import Column, Integer, String, BigInteger, Float
from sqlalchemy.orm import relationship
from app.db.session import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String(100), nullable=False)
    capital_name = Column("capital", String(100), nullable=False)
    population = Column(BigInteger, nullable=True)
    area = Column(Float, nullable=True) #Area in square kilometers
    currency = Column(String(50), nullable=True)
    continent = Column(String(50), nullable=True)

    cities = relationship("City", back_populates="country", cascade="all, delete-orphan")
    capital_city = relationship("Capital", uselist=False, back_populates="country")
    tourist_attractions = relationship("TouristAttraction", uselist=True, back_populates="country")

    @property
    def capital_city_id(self):
        return self.capital_city.city_id if self.capital_city else None


