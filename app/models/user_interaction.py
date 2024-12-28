from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attraction_id = Column(Integer, ForeignKey("tourist_attractions.id"), nullable=False)
    rating = Column(Integer, nullable=False)

    user = relationship("User", back_populates="interactions")
    attraction = relationship("TouristAttraction")