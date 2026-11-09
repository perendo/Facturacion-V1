from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ClientBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    tax_id: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    tax_id: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = None


class ClientRead(ClientBase):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime