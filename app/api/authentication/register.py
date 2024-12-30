from fastapi import Depends, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.authentication_schemas import RegisterRequest
from app.api.authentication import authentication_router
from app.service.authentication.register_service import RegisterService


@authentication_router.post("/register")
async def register_user(user_data: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    glove_model = request.app.state.glove_model
    register_service = RegisterService(db, glove_model)
    register_service.register(user_data)
