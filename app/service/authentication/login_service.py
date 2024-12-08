from sqlalchemy.orm import Session
from app.schemas.authentication_schemas import LoginRequest
from app.models.user import User
from app.utils.utils import verify_password, create_access_token
from fastapi import HTTPException


class LoginService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, user_data: LoginRequest):
        user = self.db.query(User).filter(User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token}
