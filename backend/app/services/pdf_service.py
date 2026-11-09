import qrcode
from io import BytesIO
from decimal import Decimal

from fpdf import FPDF

from ..models import Invoice, User


def _money(v) -> str:
    return f"{float(v):,.2f}"


def _qr_code_image(data: str) -> BytesIO:
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def generate_invoice_pdf(invoice: Invoice, user: User) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "FACTURA", ln=True, align="C")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Numero: {invoice.number}", ln=True)
    pdf.cell(0, 6, f"Fecha de emision: {invoice.issue_date}", ln=True)
    if invoice.due_date:
        pdf.cell(0, 6, f"Fecha de vencimiento: {invoice.due_date}", ln=True)
    pdf.cell(0, 6, f"Estado: {invoice.status.upper()}", ln=True)
    if invoice.verifactu_hash:
        pdf.cell(0, 6, f"Hash Veri*Factu: {invoice.verifactu_hash}", ln=True)
    pdf.ln(4)

    # Emisor
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Emisor", ln=True)
    pdf.set_font("Helvetica", "", 10)
    profile = getattr(user, "company_profile", None)
    if profile:
        pdf.cell(0, 6, f"{profile.legal_name}", ln=True)
        pdf.cell(0, 6, f"NIF/CIF: {profile.tax_id}", ln=True)
        pdf.cell(0, 6, f"{profile.tax_address}, {profile.postal_code} {profile.city} ({profile.province})", ln=True)
    else:
        pdf.cell(0, 6, f"{user.full_name or user.email}", ln=True)
        pdf.cell(0, 6, f"{user.email}", ln=True)
    pdf.ln(4)

    # Cliente (snapshot inmutable)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Cliente", ln=True)
    pdf.set_font("Helvetica", "", 10)
    name = invoice.recipient_name or (invoice.client.name if invoice.client else None)
    tax_id = invoice.recipient_tax_id or (invoice.client.tax_id if invoice.client else None)
    address = invoice.recipient_address or (invoice.client.address if invoice.client else None)
    if name:
        pdf.cell(0, 6, f"{name}", ln=True)
        if tax_id:
            pdf.cell(0, 6, f"NIF/CIF: {tax_id}", ln=True)
        if address:
            pdf.multi_cell(0, 6, f"Direccion: {address}")
    else:
        pdf.cell(0, 6, "Sin cliente asignado", ln=True)
    pdf.ln(4)

    # Tabla de lineas
    pdf.set_font("Helvetica", "B", 9)
    col_widths = [70, 18, 22, 18, 20, 22, 22]
    headers = ["Descripcion", "Cant.", "P. Unit.", "Desc.%", "IVA%", "Subtotal", "Total"]
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 7, h, border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for line in invoice.lines:
        pdf.cell(col_widths[0], 7, str(line.description)[:40], border=1)
        pdf.cell(col_widths[1], 7, _money(line.quantity), border=1, align="R")
        pdf.cell(col_widths[2], 7, _money(line.unit_price), border=1, align="R")
        pdf.cell(col_widths[3], 7, _money(line.discount), border=1, align="R")
        pdf.cell(col_widths[4], 7, _money(line.tax_rate), border=1, align="R")
        pdf.cell(col_widths[5], 7, _money(line.line_subtotal), border=1, align="R")
        pdf.cell(col_widths[6], 7, _money(line.line_total), border=1, align="R")
        pdf.ln()

    pdf.ln(4)
    # Totales
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(150, 6, "Subtotal:", align="R")
    pdf.cell(0, 6, _money(invoice.subtotal), ln=True, align="R")
    if float(invoice.global_discount or 0) > 0:
        pdf.cell(150, 6, f"Descuento global ({_money(invoice.global_discount)}%):", align="R")
        pdf.cell(0, 6, "", ln=True, align="R")
    pdf.cell(150, 6, "IVA:", align="R")
    pdf.cell(0, 6, _money(invoice.tax_total), ln=True, align="R")
    if float(invoice.irpf_rate or 0) > 0:
        pdf.cell(150, 6, f"IRPF ({_money(invoice.irpf_rate)}%):", align="R")
        pdf.cell(0, 6, _money(invoice.irpf_total), ln=True, align="R")
    pdf.cell(150, 6, "TOTAL:", align="R")
    pdf.cell(0, 6, _money(invoice.total), ln=True, align="R")

    # Codigo QR de cotejo tributario (Veri*Factu)
    qr_data = (
        f"{getattr(getattr(user, 'company_profile', None), 'tax_id', user.email)}|"
        f"{invoice.number}|{invoice.issue_date}|{invoice.total}|"
        f"{invoice.verifactu_hash or ''}"
    )
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Codigo QR de cotejo tributario (AEAT):", ln=True)
    qr_buf = _qr_code_image(qr_data)
    pdf.image(qr_buf, x=None, y=None, w=30, h=30, type="PNG")

    if invoice.notes:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Notas", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, str(invoice.notes))

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()
