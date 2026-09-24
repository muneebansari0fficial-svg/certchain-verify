import sys
import os
from pathlib import Path
import pymupdf as fitz  # New name


def pdf_to_image(pdf_path: str, output_path: str = None) -> str:
    """
    Convert first page of PDF to PNG image.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Default output path
    if output_path is None:
        output_path = "ai/dataset/certificate_page.png"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Open PDF
    doc = fitz.open(str(pdf_path))

    if len(doc) == 0:
        raise Exception("PDF has no pages")

    # Get first page
    page = doc[0]

    # Render at 2x scale (better quality for AI)
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)

    # Save as PNG
    pix.save(str(output_path))

    doc.close()

    return str(output_path)


# ============================================
# CLI USAGE
# ============================================

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python pdf_to_image.py <pdf_path> [output_path]")
        sys.exit(1)

    pdf_path = sys.argv[1]

    output_path = sys.argv[2] if len(sys.argv) > 2 else "ai/dataset/certificate_page.png"

    try:
        result = pdf_to_image(pdf_path, output_path)
        print(f"SUCCESS: {result}")

    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
        