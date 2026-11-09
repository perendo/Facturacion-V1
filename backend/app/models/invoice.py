from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from ..database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    number = Column(String(30), unique=True, nullable=False, index=True)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    global_discount = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    subtotal = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    tax_total = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    total = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan", order_by="InvoiceLine.id")