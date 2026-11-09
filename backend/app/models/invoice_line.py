from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from ..database import Base


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False, default=Decimal("1.00"))
    unit_price = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    discount = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    tax_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("21.00"))
    line_subtotal = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    line_tax = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    line_total = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))

    invoice = relationship("Invoice", back_populates="lines")
    product = relationship("Product", back_populates="invoice_lines")