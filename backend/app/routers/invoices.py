from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Invoice, User
from ..schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceRead, InvoiceStatusUpdate
from ..services import invoice_service, pdf_service
from ..dependencies import get_current_user
from ..rate_limit import check_rate_limit

router = APIRouter(prefix="/invoices", tags=["invoices"])


def _get_invoice(db, invoice_id, user_id):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.user_id == user_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return inv


@router.get("", response_model=List[InvoiceRead])
def list_invoices(
    request: Request,
    client_id: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    number: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    skip: Optional[int] = Query(default=None, ge=0),
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(request, "invoices_list")
    q = db.query(Invoice).filter(Invoice.user_id == current_user.id)
    if client_id is not None:
        q = q.filter(Invoice.client_id == client_id)
    if status:
        q = q.filter(Invoice.status == status)
    if date_from:
        q = q.filter(Invoice.issue_date >= date_from)
    if date_to:
        q = q.filter(Invoice.issue_date <= date_to)
    if number:
        q = q.filter(Invoice.number.ilike(f"%{number}%"))
    offset = skip if skip is not None else (page - 1) * page_size
    size = limit if limit is not None else page_size
    return q.order_by(Invoice.id.desc()).offset(offset).limit(size).all()


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(
    request: Request,
    payload: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(request, "invoices_create")
    invoice = invoice_service.create_invoice(db, current_user, payload)
    return invoice


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_invoice(db, invoice_id, current_user.id)


@router.put("/{invoice_id}", response_model=InvoiceRead)
def update_invoice(
    invoice_id: int,
    payload: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = _get_invoice(db, invoice_id, current_user.id)
    if invoice.status != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft invoices can be edited")
    return invoice_service.update_invoice(db, invoice, current_user, payload)


@router.patch("/{invoice_id}/status", response_model=InvoiceRead)
def change_status(
    invoice_id: int,
    payload: InvoiceStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = _get_invoice(db, invoice_id, current_user.id)
    invoice_service.change_status(invoice, payload.status, db=db, user=current_user)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = _get_invoice(db, invoice_id, current_user.id)
    if invoice.status != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only draft invoices can be deleted")
    db.delete(invoice)
    db.commit()
    return None


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = _get_invoice(db, invoice_id, current_user.id)
    pdf_bytes = pdf_service.generate_invoice_pdf(invoice, current_user)
    filename = f"{invoice.number}.pdf"
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )