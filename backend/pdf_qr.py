import io
from pathlib import Path
import qrcode
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def create_qr_overlay_pdf(qr_data, page_width, page_height):
    """Create PDF overlay with TRANSPARENT QR code."""

    buffer = io.BytesIO()

    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    # ------------------------------------
    # QR Code generate karo
    # ------------------------------------

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    # ✅ PIL Image banao (RGBA mode — transparent support)
    qr_img = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGBA")

    # ✅ White pixels ko transparent karo
    datas = qr_img.getdata()
    new_data = []

    for item in datas:
        # White pixels → transparent
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    qr_img.putdata(new_data)

    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # ------------------------------------
    # QR Position
    # ------------------------------------

    qr_size = 80

    # Bottom-right corner (default)
    x = page_width - qr_size - 80
    y = 100

    # ------------------------------------
    # QR draw karo (transparent support)
    # ------------------------------------

    c.drawImage(
        ImageReader(qr_buffer),
        x, y,
        width=qr_size,
        height=qr_size,
        mask='auto'  # ✅ Transparent support
    )

    c.save()
    buffer.seek(0)

    return buffer.getvalue()


def add_qr_to_pdf(pdf_path, qr_data, output_path):
    """Add transparent QR code to first page of PDF."""

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()

    first_page = reader.pages[0]

    page_width = float(first_page.mediabox.width)
    page_height = float(first_page.mediabox.height)

    overlay_pdf_bytes = create_qr_overlay_pdf(
        qr_data, page_width, page_height
    )

    overlay_reader = PdfReader(io.BytesIO(overlay_pdf_bytes))
    overlay_page = overlay_reader.pages[0]

    first_page.merge_page(overlay_page)
    writer.add_page(first_page)

    for page in reader.pages[1:]:
        writer.add_page(page)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        writer.write(f)

    return str(output_path)