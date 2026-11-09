from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from ..database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="RESTRICT"), nullable=True, index=True)

    # Numeración por usuario/serie/año (sin fuga entre inquilinos)
    series = Column(String(10), nullable=False, default="INV")
    year = Column(Integer, nullable=False, default=datetime.utcnow().year)
    sequence_number = Column(Integer, nullable=False, default=1)
    number = Column(String(50), nullable=False, index=True)

    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="draft")

    # Tipo de factura y rectificativas
    invoice_type = Column(String(20), nullable=False, default="ordinary")  # ordinary | rectification
    rectifies_invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True)
    rectification_reason = Column(Text, nullable=True)

    # Descuentos e impuestos
    global_discount = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    irpf_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    irpf_total = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    subtotal = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    tax_total = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    total = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    notes = Column(Text, nullable=True)

    # Snapshot fiscal del receptor (inmutable)
    recipient_name = Column(String(255), nullable=True)
    recipient_tax_id = Column(String(50), nullable=True)
    recipient_address = Column(Text, nullable=True)

    # Trazabilidad Veri*Factu (hash encadenado)
    previous_hash = Column(String(64), nullable=True)
    verifactu_hash = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan", order_by="InvoiceLine.id")
    rectifies = relationship("Invoice", remote_side=[id], foreign_keys=[rectifies_invoice_id])
    events = relationship("InvoiceEvent", back_populates="invoice", cascade="all, delete-orphan", order_by="InvoiceEvent.id")

    __table_args__ = (
        UniqueConstraint("user_id", "series", "year", "sequence_number", name="uq_user_invoice_sequence"),
    )
