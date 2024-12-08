from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, LargeBinary
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    description_of_interests = Column(Text, nullable=True)
    embedding = Column(LargeBinary, nullable=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True)

    country = relationship("Country")
    city = relationship("City")
    user_preferences = relationship("UserPreference", back_populates="user")
