from sqlalchemy import Column, Integer, String, BigInteger, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    area = Column(Float, nullable=True)
    population = Column(BigInteger, nullable=True)
    thumbnail = Column(String(300), nullable=True)
    description = Column(Text, nullable=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)

    country = relationship("Country", back_populates="cities")
    tourist_attractions = relationship("TouristAttraction", uselist=True, back_populates="city")
