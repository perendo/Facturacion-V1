import hashlib
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Invoice, InvoiceLine, Product, Client, CompanyProfile, InvoiceEvent
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


def calculate_verifactu_hash(
    emisor_nif: str,
    numero_factura: str,
    fecha_emision: str,
    total_factura: str,
    prev_hash: Optional[str] = None,
) -> str:
    cadena = f"{emisor_nif}|{numero_factura}|{fecha_emision}|{total_factura}|{prev_hash or ''}"
    return hashlib.sha256(cadena.encode("utf-8")).hexdigest().upper()


def reserve_invoice_number(
    db: Session, user_id: int, series: str = "INV", year: Optional[int] = None
) -> Tuple[str, str, int, int]:
    if year is None:
        year = datetime.utcnow().year
    max_seq = (
        db.query(func.max(Invoice.sequence_number))
        .filter(Invoice.user_id == user_id, Invoice.series == series, Invoice.year == year)
        .scalar()
    ) or 0
    next_seq = max_seq + 1
    number = f"{series}-{year}-{next_seq:04d}"
    return number, series, year, next_seq


def generate_invoice_number(
    db: Session, user_id: int, series: str = "INV", year: Optional[int] = None
) -> str:
    number, _, _, _ = reserve_invoice_number(db, user_id, series, year)
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
    gd = _to_decimal(invoice.global_discount)
    factor = Decimal("1") - gd / Decimal("100")
    subtotal = Decimal("0")
    tax_total = Decimal("0")
    for line in invoice.lines:
        q = _to_decimal(line.quantity)
        price = _to_decimal(line.unit_price)
        disc = _to_decimal(line.discount)
        tax = _to_decimal(line.tax_rate)
        base = q * price * (Decimal("1") - disc / Decimal("100"))
        base = base * factor
        line.line_subtotal = _q(base)
        line.line_tax = _q(base * tax / Decimal("100"))
        line.line_total = _q(line.line_subtotal + line.line_tax)
        subtotal += _to_decimal(line.line_subtotal)
        tax_total += _to_decimal(line.line_tax)
    invoice.subtotal = _q(subtotal)
    invoice.tax_total = _q(tax_total)
    invoice.total = _q(subtotal + tax_total)
    invoice.irpf_total = _q(invoice.subtotal * _to_decimal(invoice.irpf_rate) / Decimal("100"))


def _validate_product(db: Session, user_id: int, product_id: Optional[int]) -> Optional[Product]:
    if product_id is None:
        return None
    product = db.query(Product).filter(Product.id == product_id, Product.user_id == user_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def _issuer_nif(db: Session, user: User) -> str:
    profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == user.id).first()
    if profile and profile.tax_id:
        return profile.tax_id
    return user.email


def _set_recipient_snapshot(invoice: Invoice, client: Optional[Client]) -> None:
    if client is None:
        return
    invoice.recipient_name = client.name
    invoice.recipient_tax_id = client.tax_id
    invoice.recipient_address = client.address


def _compute_verifactu(db: Session, invoice: Invoice, user: User) -> None:
    prev = (
        db.query(Invoice.verifactu_hash)
        .filter(Invoice.user_id == user.id, Invoice.id != invoice.id)
        .order_by(Invoice.id.desc())
        .first()
    )
    previous_hash = prev[0] if prev else None
    invoice.previous_hash = previous_hash
    invoice.verifactu_hash = calculate_verifactu_hash(
        _issuer_nif(db, user),
        invoice.number,
        str(invoice.issue_date),
        str(invoice.total),
        previous_hash,
    )


def create_invoice(db: Session, user: User, payload: InvoiceCreate) -> Invoice:
    client = None
    if payload.client_id is not None:
        client = db.query(Client).filter(Client.id == payload.client_id, Client.user_id == user.id).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    year = payload.issue_date.year if payload.issue_date else datetime.utcnow().year
    # retry on unique constraint race
    for _ in range(5):
        number, series, yr, seq = reserve_invoice_number(db, user.id, "INV", year)
        invoice = Invoice(
            user_id=user.id,
            client_id=payload.client_id,
            series=series,
            year=yr,
            sequence_number=seq,
            number=number,
            issue_date=payload.issue_date,
            due_date=payload.due_date,
            status="draft",
            invoice_type=getattr(payload, "invoice_type", None) or "ordinary",
            rectifies_invoice_id=getattr(payload, "rectifies_invoice_id", None),
            rectification_reason=getattr(payload, "rectification_reason", None),
            global_discount=_to_decimal(payload.global_discount),
            irpf_rate=_to_decimal(getattr(payload, "irpf_rate", 0.0)),
            notes=payload.notes,
        )
        _set_recipient_snapshot(invoice, client)
        db.add(invoice)
        try:
            db.flush()
            break
        except Exception:
            db.rollback()
            continue
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate invoice number")

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
    _compute_verifactu(db, invoice, user)
    db.add(InvoiceEvent(
        invoice_id=invoice.id,
        event_type="created",
        changed_by_user_id=user.id,
        new_values=json.dumps({"number": invoice.number, "status": invoice.status, "total": str(invoice.total)}),
    ))
    db.commit()
    db.refresh(invoice)
    return invoice


def _log_invoice_event(db: Session, invoice: Invoice, user: User, event_type: str, previous: Optional[dict] = None, new: Optional[dict] = None) -> None:
    db.add(InvoiceEvent(
        invoice_id=invoice.id,
        event_type=event_type,
        changed_by_user_id=user.id,
        previous_values=json.dumps(previous) if previous else None,
        new_values=json.dumps(new) if new else None,
    ))


def update_invoice(db: Session, invoice: Invoice, user: User, payload: InvoiceUpdate) -> Invoice:
    if payload.client_id is not None:
        if payload.client_id == 0:
            invoice.client_id = None
        else:
            client = db.query(Client).filter(Client.id == payload.client_id, Client.user_id == user.id).first()
            if not client:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
            invoice.client_id = payload.client_id
            _set_recipient_snapshot(invoice, client)

    if payload.issue_date is not None:
        invoice.issue_date = payload.issue_date
    if payload.due_date is not None:
        invoice.due_date = payload.due_date
    if payload.global_discount is not None:
        invoice.global_discount = _to_decimal(payload.global_discount)
    if payload.notes is not None:
        invoice.notes = payload.notes
    if getattr(payload, "irpf_rate", None) is not None:
        invoice.irpf_rate = _to_decimal(payload.irpf_rate)

    if payload.lines is not None:
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
    _log_invoice_event(db, invoice, user, "updated",
                       previous={"status": invoice.status, "total": str(invoice.total)},
                       new={"status": invoice.status, "total": str(invoice.total)})
    db.commit()
    db.refresh(invoice)
    return invoice


VALID_TRANSITIONS = {
    "draft": {"sent", "cancelled"},
    "sent": {"paid", "cancelled"},
    "paid": set(),
    "cancelled": set(),
}


def change_status(invoice: Invoice, new_status: str, db: Session = None, user: User = None) -> None:
    if new_status not in {"draft", "sent", "paid", "cancelled"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    if new_status not in VALID_TRANSITIONS.get(invoice.status, set()) and new_status != invoice.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {invoice.status} to {new_status}",
        )
    previous_status = invoice.status
    invoice.status = new_status
    if db is not None and user is not None:
        _log_invoice_event(db, invoice, user, "status_changed",
                           previous={"status": previous_status},
                           new={"status": new_status})
