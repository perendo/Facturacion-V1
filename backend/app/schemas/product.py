from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    unit_price: float = Field(default=0.0, ge=0)
    tax_rate: float = Field(default=21.0, ge=0, le=100)
    unit: Optional[str] = Field(default=None, max_length=50)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    unit_price: Optional[float] = Field(default=None, ge=0)
    tax_rate: Optional[float] = Field(default=None, ge=0, le=100)
    unit: Optional[str] = Field(default=None, max_length=50)


class ProductRead(ProductBase):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime