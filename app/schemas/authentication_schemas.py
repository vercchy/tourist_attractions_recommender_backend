from pydantic import BaseModel, EmailStr
from typing import List, Optional


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    email: EmailStr
    password: str
    country_id: int
    city_id: Optional[int] = None
    interests: Optional[str] = None
    preferences: List[int]  #category ids the user chooses


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
