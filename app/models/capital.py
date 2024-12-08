from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Capital(Base):
    __tablename__ = "capitals"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)

    country = relationship("Country", back_populates="capital_city")


