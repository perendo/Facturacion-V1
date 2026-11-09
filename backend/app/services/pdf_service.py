from io import BytesIO
from decimal import Decimal

from fpdf import FPDF

from ..models import Invoice, User


def _money(v) -> str:
    return f"{float(v):,.2f}"


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
    pdf.ln(4)

    # Emisor
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Emisor", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"{user.full_name or user.email}", ln=True)
    pdf.cell(0, 6, f"{user.email}", ln=True)
    pdf.ln(4)

    # Cliente
    client = invoice.client
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Cliente", ln=True)
    pdf.set_font("Helvetica", "", 10)
    if client:
        pdf.cell(0, 6, f"{client.name}", ln=True)
        if client.tax_id:
            pdf.cell(0, 6, f"NIF/CIF: {client.tax_id}", ln=True)
        if client.email:
            pdf.cell(0, 6, f"Email: {client.email}", ln=True)
        if client.phone:
            pdf.cell(0, 6, f"Telefono: {client.phone}", ln=True)
        if client.address:
            pdf.multi_cell(0, 6, f"Direccion: {client.address}")
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
    pdf.cell(150, 6, "TOTAL:", align="R")
    pdf.cell(0, 6, _money(invoice.total), ln=True, align="R")

    if invoice.notes:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, "Notas", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, str(invoice.notes))

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()