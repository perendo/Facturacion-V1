from pydantic import BaseModel, Field
from typing import Optional


class CompanyProfileBase(BaseModel):
    legal_name: str = Field(min_length=1, max_length=255)
    tax_id: str = Field(min_length=1, max_length=20)
    tax_address: str = Field(min_length=1, max_length=255)
    postal_code: str = Field(min_length=1, max_length=10)
    city: str = Field(min_length=1, max_length=100)
    province: str = Field(min_length=1, max_length=100)
    country: str = Field(default="España", max_length=100)


class CompanyProfileCreate(CompanyProfileBase):
    pass


class CompanyProfileUpdate(BaseModel):
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    tax_address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None


class CompanyProfileRead(CompanyProfileBase):
    model_config = {"from_attributes": True}
    id: int
    user_id: int
