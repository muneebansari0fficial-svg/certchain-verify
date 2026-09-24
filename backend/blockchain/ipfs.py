import os
import requests
from dotenv import load_dotenv

from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

PINATA_JWT = os.getenv("PINATA_JWT")

PINATA_UPLOAD_URL = "https://uploads.pinata.cloud/v3/files"


def upload_to_ipfs(file_bytes: bytes, filename: str) -> str:
    """
    Upload certificate PDF to IPFS via Pinata.
    Returns IPFS CID.
    """

    if not PINATA_JWT:
        raise Exception("PINATA_JWT missing in .env file")

    headers = {
        "Authorization": f"Bearer {PINATA_JWT}"
    }

    files = {
        "file": (filename, file_bytes, "application/pdf")
    }

    response = requests.post(
        PINATA_UPLOAD_URL,
        headers=headers,
        files=files,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(
            f"IPFS upload failed: {response.status_code} - {response.text}"
        )

    data = response.json()

    cid = data.get("data", {}).get("cid")

    if not cid:
        raise Exception(f"IPFS CID not found in response: {data}")

    return cid