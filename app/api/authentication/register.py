from app.api.routers.authentication_router import authentication_router
from app.schemas.authentication_schemas import RegisterRequest
from sqlalchemy.orm import Session
from fastapi import Depends, Request
from app.db.session import get_db
from app.service.authentication.register_service import RegisterService


@authentication_router.post("/register")
async def register_user(user_data: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    glove_model = request.app.state.glove_model
    register_service = RegisterService(db, glove_model=glove_model)
    register_service.register(user_data)
