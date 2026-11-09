from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def _strong_password(cls, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise ValueError("password must contain an uppercase letter")
        if not any(c.islower() for c in value):
            raise ValueError("password must contain a lowercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("password must contain a digit")
        return value
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime