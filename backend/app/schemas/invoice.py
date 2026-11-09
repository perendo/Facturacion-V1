from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class InvoiceLineCreate(BaseModel):
    product_id: Optional[int] = None
    description: str = Field(min_length=1, max_length=255)
    quantity: float = Field(default=1.0, gt=0)
    unit_price: float = Field(default=0.0, ge=0)
    discount: float = Field(default=0.0, ge=0, le=100)
    tax_rate: float = Field(default=21.0, ge=0, le=100)


class InvoiceLineRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    invoice_id: int
    product_id: Optional[int] = None
    description: str
    quantity: float
    unit_price: float
    discount: float
    tax_rate: float
    line_subtotal: float
    line_tax: float
    line_total: float


class InvoiceBase(BaseModel):
    client_id: Optional[int] = None
    issue_date: date
    due_date: Optional[date] = None
    global_discount: float = Field(default=0.0, ge=0, le=100)
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    lines: List[InvoiceLineCreate] = Field(default_factory=list)


class InvoiceUpdate(BaseModel):
    client_id: Optional[int] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    global_discount: Optional[float] = Field(default=None, ge=0, le=100)
    notes: Optional[str] = None
    lines: Optional[List[InvoiceLineCreate]] = None


class InvoiceRead(InvoiceBase):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    number: str
    status: str
    subtotal: float
    tax_total: float
    total: float
    created_at: datetime
    updated_at: datetime
    lines: List[InvoiceLineRead] = Field(default_factory=list)


class InvoiceStatusUpdate(BaseModel):
    status: str
