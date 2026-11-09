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
    irpf_rate: float = Field(default=0.0, ge=0, le=100)
    invoice_type: Optional[str] = Field(default="ordinary")
    rectifies_invoice_id: Optional[int] = None
    rectification_reason: Optional[str] = None
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    lines: List[InvoiceLineCreate] = Field(default_factory=list)


class InvoiceUpdate(BaseModel):
    client_id: Optional[int] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    global_discount: Optional[float] = Field(default=None, ge=0, le=100)
    irpf_rate: Optional[float] = Field(default=None, ge=0, le=100)
    notes: Optional[str] = None
    lines: Optional[List[InvoiceLineCreate]] = None


class InvoiceRead(InvoiceBase):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    number: str
    series: str = "INV"
    year: int
    sequence_number: int
    status: str
    invoice_type: str = "ordinary"
    rectifies_invoice_id: Optional[int] = None
    rectification_reason: Optional[str] = None
    irpf_rate: float = 0.0
    irpf_total: float = 0.0
    subtotal: float
    tax_total: float
    total: float
    recipient_name: Optional[str] = None
    recipient_tax_id: Optional[str] = None
    recipient_address: Optional[str] = None
    previous_hash: Optional[str] = None
    verifactu_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    lines: List[InvoiceLineRead] = Field(default_factory=list)


class InvoiceStatusUpdate(BaseModel):
    status: str
