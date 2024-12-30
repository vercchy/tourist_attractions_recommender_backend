from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attraction_id = Column(Integer, ForeignKey("tourist_attractions.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="interactions")
    attraction = relationship("TouristAttraction")