import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


def invoice_pdf(invoice, order, customer, printer) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    c.setFillColorRGB(0.12, 0.12, 0.18)
    c.rect(0, h - 30 * mm, w, 30 * mm, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20 * mm, h - 18 * mm, "Printer Management System")
    c.setFont("Helvetica", 11)
    c.drawString(20 * mm, h - 25 * mm, "Official Invoice")

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20 * mm, h - 45 * mm, f"Invoice: {invoice.invoice_number}")
    c.setFont("Helvetica", 11)
    c.drawString(20 * mm, h - 52 * mm, f"Date: {invoice.created_at.strftime('%Y-%m-%d %H:%M')}")
    c.drawString(20 * mm, h - 58 * mm, f"Order #: {order.id}   Status: {order.status}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, h - 72 * mm, "Bill To")
    c.setFont("Helvetica", 11)
    c.drawString(20 * mm, h - 78 * mm, f"{customer.full_name}")
    c.drawString(20 * mm, h - 84 * mm, f"{customer.email}  |  {customer.phone}")
    c.drawString(20 * mm, h - 90 * mm, f"{order.address}")

    y = h - 110 * mm
    c.setFillColorRGB(0.95, 0.95, 0.97)
    c.rect(20 * mm, y, w - 40 * mm, 10 * mm, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(22 * mm, y + 3 * mm, "Item")
    c.drawString(110 * mm, y + 3 * mm, "Qty")
    c.drawString(130 * mm, y + 3 * mm, "Unit")
    c.drawString(160 * mm, y + 3 * mm, "Amount")

    y -= 10 * mm
    c.setFont("Helvetica", 11)
    c.drawString(22 * mm, y, printer.name)
    c.drawString(110 * mm, y, str(order.quantity))
    c.drawString(130 * mm, y, f"{order.unit_price:.2f}")
    c.drawString(160 * mm, y, f"{order.subtotal:.2f}")

    y -= 20 * mm
    c.setFont("Helvetica", 11)
    c.drawRightString(170 * mm, y, f"Subtotal: {invoice.subtotal:.2f}")
    c.drawRightString(170 * mm, y - 6 * mm, f"GST (10%): {invoice.gst:.2f}")
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(170 * mm, y - 14 * mm, f"Total: {invoice.total:.2f}")

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.4, 0.4, 0.45)
    c.drawString(20 * mm, 15 * mm, "Thank you for your business.")
    c.showPage()
    c.save()
    return buf.getvalue()


def report_pdf(title: str, rows: list[tuple[str, str]]) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    c.setFillColorRGB(0.12, 0.12, 0.18)
    c.rect(0, h - 25 * mm, w, 25 * mm, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20 * mm, h - 16 * mm, title)
    c.setFillColorRGB(0, 0, 0)
    y = h - 40 * mm
    c.setFont("Helvetica", 12)
    for label, value in rows:
        c.drawString(25 * mm, y, label)
        c.drawRightString(w - 25 * mm, y, str(value))
        y -= 8 * mm
    c.showPage()
    c.save()
    return buf.getvalue()
