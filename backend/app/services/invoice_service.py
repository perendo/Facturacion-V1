from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import Invoice, InvoiceLine, Product, Client
from ..schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceLineCreate
from ..models.user import User


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _q(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def generate_invoice_number(db: Session, user_id: int, year: Optional[int] = None) -> str:
    if year is None:
        year = datetime.utcnow().year
    prefix = f"INV-{year}-"
    existing = (
        db.query(Invoice)
        .filter(Invoice.user_id == user_id, Invoice.number.like(f"{prefix}%"))
        .count()
    )
    seq = existing + 1
    # ensure uniqueness
    while True:
        number = f"{prefix}{seq:04d}"
        clash = db.query(Invoice).filter(Invoice.number == number).first()
        if not clash:
            break
        seq += 1
    return number


def calculate_line(quantity, unit_price, discount, tax_rate) -> dict:
    q = _to_decimal(quantity)
    price = _to_decimal(unit_price)
    disc = _to_decimal(discount)
    tax = _to_decimal(tax_rate)
    base = q * price * (Decimal("1") - disc / Decimal("100"))
    line_subtotal = _q(base)
    line_tax = _q(base * tax / Decimal("100"))
    line_total = _q(line_subtotal + line_tax)
    return {
        "line_subtotal": line_subtotal,
        "line_tax": line_tax,
        "line_total": line_total,
    }


def recalculate_invoice(invoice: Invoice) -> None:
    subtotal = Decimal("0")
    tax_total = Decimal("0")
    for line in invoice.lines:
        vals = calculate_line(line.quantity, line.unit_price, line.discount, line.tax_rate)
        line.line_subtotal = vals["line_subtotal"]
        line.line_tax = vals["line_tax"]
        line.line_total = vals["line_total"]
        subtotal += _to_decimal(line.line_subtotal)
        tax_total += _to_decimal(line.line_tax)
    subtotal = _q(subtotal)
    tax_total = _q(tax_total)
    gd = _to_decimal(invoice.global_discount)
    factor = Decimal("1") - gd / Decimal("100")
    subtotal_discounted = _q(subtotal * factor)
    tax_total = _q(tax_total * factor)
    invoice.subtotal = subtotal
    invoice.tax_total = tax_total
    invoice.total = _q(subtotal_discounted + tax_total)


def _validate_product(db: Session, user_id: int, product_id: Optional[int]) -> Optional[Product]:
    if product_id is None:
        return None
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def create_invoice(db: Session, user: User, payload: InvoiceCreate) -> Invoice:
    client = None
    if payload.client_id is not None:
        client = db.query(Client).filter(Client.id == payload.client_id, Client.user_id == user.id).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    year = payload.issue_date.year if payload.issue_date else datetime.utcnow().year
    number = generate_invoice_number(db, user.id, year)

    invoice = Invoice(
        user_id=user.id,
        client_id=payload.client_id,
        number=number,
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        status="draft",
        global_discount=_to_decimal(payload.global_discount),
        notes=payload.notes,
    )
    db.add(invoice)
    db.flush()

    for line_in in payload.lines:
        _validate_product(db, user.id, line_in.product_id)
        line = InvoiceLine(
            invoice_id=invoice.id,
            product_id=line_in.product_id,
            description=line_in.description,
            quantity=_to_decimal(line_in.quantity),
            unit_price=_to_decimal(line_in.unit_price),
            discount=_to_decimal(line_in.discount),
            tax_rate=_to_decimal(line_in.tax_rate),
        )
        db.add(line)

    db.flush()
    recalculate_invoice(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def update_invoice(db: Session, invoice: Invoice, user: User, payload: InvoiceUpdate) -> Invoice:
    if payload.client_id is not None:
        if payload.client_id == 0:
            invoice.client_id = None
        else:
            client = db.query(Client).filter(Client.id == payload.client_id, Client.user_id == user.id).first()
            if not client:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
            invoice.client_id = payload.client_id

    if payload.issue_date is not None:
        invoice.issue_date = payload.issue_date
    if payload.due_date is not None:
        invoice.due_date = payload.due_date
    if payload.global_discount is not None:
        invoice.global_discount = _to_decimal(payload.global_discount)
    if payload.notes is not None:
        invoice.notes = payload.notes

    if payload.lines is not None:
        # replace lines
        for existing in list(invoice.lines):
            db.delete(existing)
        db.flush()
        for line_in in payload.lines:
            _validate_product(db, user.id, line_in.product_id)
            line = InvoiceLine(
                invoice_id=invoice.id,
                product_id=line_in.product_id,
                description=line_in.description,
                quantity=_to_decimal(line_in.quantity),
                unit_price=_to_decimal(line_in.unit_price),
                discount=_to_decimal(line_in.discount),
                tax_rate=_to_decimal(line_in.tax_rate),
            )
            db.add(line)
        db.flush()

    recalculate_invoice(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


VALID_TRANSITIONS = {
    "draft": {"sent", "cancelled"},
    "sent": {"paid", "cancelled"},
    "paid": set(),
    "cancelled": set(),
}


def change_status(invoice: Invoice, new_status: str) -> None:
    if new_status not in {"draft", "sent", "paid", "cancelled"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    if new_status not in VALID_TRANSITIONS.get(invoice.status, set()) and new_status != invoice.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {invoice.status} to {new_status}",
        )
    invoice.status = new_status