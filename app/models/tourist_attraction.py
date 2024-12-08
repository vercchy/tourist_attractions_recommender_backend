from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class TouristAttraction(Base):
    __tablename__ = "tourist_attractions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    thumbnail = Column(String(500), nullable=True)
    linktowebsite = Column(String(300), nullable=True)
    linktowikipedia = Column(String(300), nullable=True)
    comment = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)

    country = relationship("Country", back_populates="tourist_attractions")
    city = relationship("City", back_populates="tourist_attractions")