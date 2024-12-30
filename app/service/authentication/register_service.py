from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.category import Category
from app.schemas.authentication_schemas import RegisterRequest
from app.utils.auth import hash_password
from app.service.embedding import compute_embedding
from datetime import datetime


class RegisterService:
    def __init__(self, db: Session, glove_model):
        self.db = db
        self.glove_model = glove_model

    def _create_user(self, user_data: RegisterRequest) -> User:
        hashed_password = hash_password(user_data.password)
        date_of_birth = datetime.strptime(user_data.date_of_birth, "%Y-%m-%d").date()
        embedding = self.load_model_and_calculate_user_embedding(user_data.interests, user_data.preferences)
        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            date_of_birth=date_of_birth,
            email=user_data.email,
            password=hashed_password,
            description_of_interests=user_data.interests,
            embedding=embedding,
            country_id=user_data.country_id,
            city_id=user_data.city_id
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def _add_user_preferences(self, preferences: list[int], user_id: int):
        for category_id in preferences:
            preference = UserPreference(user_id=user_id, category_id=category_id)
            self.db.add(preference)
            self.db.flush()
        self.db.commit()

    def register(self, user_data: RegisterRequest):
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        new_user = self._create_user(user_data)
        self._add_user_preferences(user_data.preferences, new_user.id)

    def load_model_and_calculate_user_embedding(self, interests: str, preferences: list[int]) -> bytes:
        preferences_descriptions = self.get_preferences_descriptions(preferences)
        combined_desc_of_user = f"{preferences_descriptions} {interests or ''}".strip()
        embedding = compute_embedding(combined_desc_of_user, self.glove_model).tobytes()
        return embedding

    def get_preferences_descriptions(self, preferences: list[int]) -> str:
        categories = self.db.query(Category).filter(Category.id.in_(preferences)).all()
        return " ".join(category.description for category in categories)
