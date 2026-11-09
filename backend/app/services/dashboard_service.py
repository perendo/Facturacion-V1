from decimal import Decimal
from sqlalchemy.orm import Session
from ..models import Invoice


def get_summary(db: Session, user_id: int) -> dict:
    invoices = db.query(Invoice).filter(Invoice.user_id == user_id).all()
    total_invoiced = Decimal("0")
    total_paid = Decimal("0")
    total_pending = Decimal("0")
    counts = {"draft": 0, "sent": 0, "paid": 0, "cancelled": 0}
    for inv in invoices:
        total = Decimal(str(inv.total or 0))
        total_invoiced += total
        st = inv.status
        if st in counts:
            counts[st] += 1
        if st == "paid":
            total_paid += total
        elif st in ("sent", "draft"):
            total_pending += total
    return {
        "total_invoiced": total_invoiced,
        "total_paid": total_paid,
        "total_pending": total_pending,
        "count_by_status": counts,
    }