from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models import Invoice


def get_summary(db: Session, user_id: int) -> dict:
    base = db.query(Invoice).filter(Invoice.user_id == user_id)

    total_invoiced = (
        base.filter(Invoice.status.in_(["sent", "paid"]))
        .with_entities(func.coalesce(func.sum(Invoice.total), 0))
        .scalar()
    )
    total_paid = (
        base.filter(Invoice.status == "paid")
        .with_entities(func.coalesce(func.sum(Invoice.total), 0))
        .scalar()
    )
    total_pending = (
        base.filter(Invoice.status == "sent")
        .with_entities(func.coalesce(func.sum(Invoice.total), 0))
        .scalar()
    )

    counts = {"draft": 0, "sent": 0, "paid": 0, "cancelled": 0}
    for status_name, cnt in base.with_entities(Invoice.status, func.count()).group_by(Invoice.status).all():
        if status_name in counts:
            counts[status_name] = cnt

    return {
        "total_invoiced": Decimal(str(total_invoiced or 0)),
        "total_paid": Decimal(str(total_paid or 0)),
        "total_pending": Decimal(str(total_pending or 0)),
        "count_by_status": counts,
    }
