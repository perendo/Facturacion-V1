from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class InvoiceEvent(Base):
    __tablename__ = "invoice_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # created | updated | status_changed | deleted | pdf_downloaded
    changed_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    previous_values = Column(Text, nullable=True)  # JSON snapshot antes del cambio
    new_values = Column(Text, nullable=True)       # JSON snapshot después del cambio
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    invoice = relationship("Invoice", back_populates="events")
    user = relationship("User")
