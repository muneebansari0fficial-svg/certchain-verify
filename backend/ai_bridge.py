import subprocess
import os
import sys


def run_ai_on_pdf(pdf_path: str) -> dict:
    """Convert PDF to image, run AI prediction, return risk score."""

    image_path = "ai/dataset/certificate_page.png"

    # Step 1: PDF → Image
    convert_result = subprocess.run(
        [sys.executable, "ai/pdf_to_image.py", pdf_path, image_path],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )

    if convert_result.returncode != 0:
        return {
            "available": False,
            "error": f"PDF conversion failed: {convert_result.stderr}"
        }

    # Step 2: AI prediction
    predict_result = subprocess.run(
        [sys.executable, "ai/predict.py", image_path],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )

    if predict_result.returncode != 0:
        return {
            "available": False,
            "error": f"AI prediction failed: {predict_result.stderr}"
        }

    # Step 3: Parse output
    output = predict_result.stdout

    risk_score = None
    category = "UNKNOWN"
    forged_proba = None

    for line in output.splitlines():
        if line.startswith("AI_RISK_SCORE="):
            risk_score = int(line.split("=")[1])
        elif line.startswith("AI_CATEGORY="):
            category = line.split("=")[1]
        elif line.startswith("AI_FORGED_PROBABILITY="):
            forged_proba = float(line.split("=")[1])

    if risk_score is None:
        return {
            "available": False,
            "error": "Could not parse AI risk score"
        }

    return {
        "available": True,
        "risk_score": risk_score,
        "risk_category": category,
        "forged_probability": forged_proba
    }