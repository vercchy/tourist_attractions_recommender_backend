from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.authentication_schemas import LoginRequest, TokenResponse
from app.api.authentication import authentication_router
from app.service.authentication.login_service import LoginService


@authentication_router.post("/login", response_model=TokenResponse)
async def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    login_service = LoginService(db)
    return login_service.login(user_data)
