import qrcode
import io
import base64
from pathlib import Path


def generate_qr_base64(data: str) -> str:
    """
    Generate QR code from string.
    Returns base64-encoded PNG image.
    """

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    img_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return f"data:image/png;base64,{img_base64}"


def generate_qr_file(data: str, output_path: str) -> str:
    """
    Generate QR code and save as PNG file.
    Returns file path.
    """

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    img.save(output_path)

    return output_path