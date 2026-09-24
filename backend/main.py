from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import hashlib
import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

from backend.ai_bridge import run_ai_on_pdf
from backend.blockchain.ipfs import upload_to_ipfs
from backend.blockchain.issue_certificate import issue_certificate_on_chain
from backend.qr_generator import generate_qr_base64
from backend.pdf_qr import add_qr_to_pdf


app = FastAPI(
    title="CertChain Verify API",
    description="Blockchain-based Academic Certificate Verification System",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


RPC_URL = "http://127.0.0.1:8545"

CONTRACT_ADDRESS = "0x5fbdb2315678afecb367f032d93f642f64180aa3"

INSTITUTION_PASSWORD = os.getenv("INSTITUTION_PASSWORD", "certchain2026")

INSTITUTION_NAME = "University of Azad Jammu & Kashmir (UAJK)"


# ========================================
# LOAD CONTRACT ABI
# ========================================

with open(
    "backend/blockchain/contract_abi.json",
    "r",
    encoding="utf-8"
) as f:
    CONTRACT_ABI = json.load(f)


# ========================================
# BLOCKCHAIN CONNECTION
# ========================================

w3 = Web3(Web3.HTTPProvider(RPC_URL))

contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=CONTRACT_ABI
)


# ========================================
# ROOT
# ========================================

@app.get("/")
def root():
    return {
        "message": "CertChain Verify API is running",
        "status": "success"
    }


# ========================================
# HEALTH
# ========================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "blockchain_connected": w3.is_connected()
    }


# ========================================
# LOGIN
# ========================================

INSTITUTION_USERNAME = os.getenv("INSTITUTION_USERNAME", "uajk_admin")

@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):

    if username != INSTITUTION_USERNAME:
        return {
            "status": "error",
            "message": "Invalid username"
        }

    if password != INSTITUTION_PASSWORD:
        return {
            "status": "error",
            "message": "Invalid password"
        }

    return {
        "status": "success",
        "institution_name": INSTITUTION_NAME,
        "message": "Login successful"
    }


# ========================================
# VERIFY CERTIFICATE
# ========================================

@app.post("/verify")
async def verify_certificate(
    file: UploadFile = File(...)
):

    if file.content_type != "application/pdf":
        return {
            "status": "error",
            "message": "Only PDF files are allowed"
        }

    file_data = await file.read()

    sha256_hash = hashlib.sha256(file_data).hexdigest()

    doc_hash = bytes.fromhex(sha256_hash)

    upload_dir = "backend/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(file_data)

    if not w3.is_connected():
        return {
            "status": "error",
            "message": "Blockchain connection failed"
        }

    result = contract.functions.verify(doc_hash).call()

    exists = result[0]
    valid = result[1]
    issuer = result[2]
    issuer_name = result[3]
    issued_at = result[4]
    revoked_at = result[5]
    ipfs_cid = result[6]
    blockchain_ai_risk = result[7]

    if exists and valid:
        return {
            "status": "success",
            "filename": file.filename,
            "sha256": sha256_hash,
            "certificate_status": "AUTHENTIC",
            "blockchain": {
                "exists": exists,
                "valid": valid,
                "issuer": issuer,
                "issuer_name": issuer_name,
                "issued_at": issued_at,
                "revoked_at": revoked_at,
                "ipfs_cid": ipfs_cid,
                "ai_risk_score": blockchain_ai_risk
            },
            "ai": {
                "analysis": "Blockchain-registered certificate",
                "risk_score": blockchain_ai_risk,
                "risk_category": "REGISTERED"
            }
        }

    if exists and not valid:
        return {
            "status": "success",
            "filename": file.filename,
            "sha256": sha256_hash,
            "certificate_status": "REVOKED / INVALID",
            "blockchain": {
                "exists": exists,
                "valid": valid,
                "issuer": issuer,
                "issuer_name": issuer_name,
                "issued_at": issued_at,
                "revoked_at": revoked_at,
                "ipfs_cid": ipfs_cid,
                "ai_risk_score": blockchain_ai_risk
            },
            "ai": {
                "analysis": "Certificate has been revoked",
                "risk_score": blockchain_ai_risk,
                "risk_category": "REVOKED"
            }
        }

    ai_result = run_ai_on_pdf(file_path)

    if ai_result.get("available"):
        return {
            "status": "success",
            "filename": file.filename,
            "sha256": sha256_hash,
            "certificate_status": "NOT REGISTERED",
            "blockchain": {
                "exists": False,
                "valid": False,
                "issuer": "",
                "issuer_name": "",
                "issued_at": 0,
                "revoked_at": 0,
                "ipfs_cid": "",
                "ai_risk_score": 0
            },
            "ai": {
                "risk_score": ai_result["risk_score"],
                "risk_category": ai_result["risk_category"],
                "forged_probability": ai_result["forged_probability"],
                "analysis": "AI forensic analysis performed"
            }
        }

    else:
        return {
            "status": "success",
            "filename": file.filename,
            "sha256": sha256_hash,
            "certificate_status": "NOT REGISTERED",
            "blockchain": {
                "exists": False,
                "valid": False,
                "issuer": "",
                "issuer_name": "",
                "issued_at": 0,
                "revoked_at": 0,
                "ipfs_cid": "",
                "ai_risk_score": 0
            },
            "ai": {
                "risk_score": None,
                "risk_category": "AI_ERROR",
                "analysis": ai_result.get("error", "Unknown AI error")
            }
        }


# ========================================
# ISSUE CERTIFICATE
# ========================================

@app.post("/issue")
async def issue_certificate(
    file: UploadFile = File(...),
    student_ref: str = Form(...)
):

    if file.content_type != "application/pdf":
        return {
            "status": "error",
            "message": "Only PDF files are allowed"
        }

    file_data = await file.read()

    sha256_hash = hashlib.sha256(file_data).hexdigest()

    upload_dir = "backend/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(file_data)

    if not w3.is_connected():
        return {
            "status": "error",
            "message": "Blockchain connection failed"
        }

    doc_hash_bytes = bytes.fromhex(sha256_hash)

    existing = contract.functions.verify(doc_hash_bytes).call()

    if existing[0]:
        return {
            "status": "error",
            "message": "Certificate already issued on blockchain",
            "sha256": sha256_hash
        }

    student_ref_hash = hashlib.sha256(
        student_ref.encode()
    ).hexdigest()

    ai_result = run_ai_on_pdf(file_path)

    if ai_result.get("available"):
        ai_risk_score = ai_result["risk_score"]

        if ai_risk_score >= 75:
            return {
                "status": "error",
                "message": f"Certificate blocked: AI risk score {ai_risk_score} is too high",
                "ai_risk_score": ai_risk_score,
                "ai_risk_category": ai_result["risk_category"]
            }
    else:
        ai_risk_score = 5

     
        # @IPFS upload — agar internet nahi hai to skip jb deploy krny lgo to ya code remove kr du ga
    ipfs_cid = ""

    try:
        ipfs_cid = upload_to_ipfs(file_data, file.filename)
    except Exception as e:
        print(f"IPFS upload failed (offline mode): {e}")
        ipfs_cid = "OFFLINE_MODE"

    try:
        tx_hash = issue_certificate_on_chain(
            doc_hash_hex=sha256_hash,
            student_ref_hex=student_ref_hash,
            ipfs_cid=ipfs_cid,
            ai_risk_score=ai_risk_score
        )
    except Exception as e:
        return {
            "status": "error",
            "message": f"Blockchain issue failed: {str(e)}"
        }

    verification_url = f"http://localhost:5173/verify/{sha256_hash}"

    qr_code_data = generate_qr_base64(verification_url)

    qr_pdf_filename = f"certificate_with_qr_{sha256_hash[:16]}.pdf"

    qr_pdf_path = os.path.join("backend/uploads", qr_pdf_filename)

    qr_pdf_url = None

    try:
        add_qr_to_pdf(
            pdf_path=file_path,
            qr_data=verification_url,
            output_path=qr_pdf_path
        )

        qr_pdf_url = f"http://127.0.0.1:8000/download/{qr_pdf_filename}"

    except Exception as e:
        print(f"QR PDF generation failed: {e}")

    return {
        "status": "success",
        "message": "Certificate issued successfully",
        "sha256": sha256_hash,
        "student_ref": student_ref,
        "ipfs_cid": ipfs_cid,
        "tx_hash": tx_hash,
        "ai_risk_score": ai_risk_score,
        "verification_url": verification_url,
        "qr_code": qr_code_data,
        "qr_pdf_url": qr_pdf_url
    }


# ========================================
# VERIFY BY HASH (for QR codes)
# ========================================

@app.get("/verify/{sha256_hash}")
async def verify_by_hash(sha256_hash: str):

    if len(sha256_hash) != 64:
        return {
            "status": "error",
            "message": "Invalid SHA-256 hash"
        }

    if not w3.is_connected():
        return {
            "status": "error",
            "message": "Blockchain connection failed"
        }

    try:
        doc_hash_bytes = bytes.fromhex(sha256_hash)
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid hash format"
        }

    result = contract.functions.verify(doc_hash_bytes).call()

    exists = result[0]
    valid = result[1]
    issuer = result[2]
    issuer_name = result[3]
    issued_at = result[4]
    revoked_at = result[5]
    ipfs_cid = result[6]
    blockchain_ai_risk = result[7]

    if exists and valid:
        status = "AUTHENTIC"
    elif exists and not valid:
        status = "REVOKED"
    else:
        status = "NOT REGISTERED"

    return {
        "status": "success",
        "sha256": sha256_hash,
        "certificate_status": status,
        "blockchain": {
            "exists": exists,
            "valid": valid,
            "issuer": issuer,
            "issuer_name": issuer_name,
            "issued_at": issued_at,
            "revoked_at": revoked_at,
            "ipfs_cid": ipfs_cid,
            "ai_risk_score": blockchain_ai_risk
        }
    }


# ========================================
# DOWNLOAD FILE
# ========================================

@app.get("/download/{filename}")
async def download_file(filename: str):

    file_path = os.path.join("backend/uploads", filename)

    if not os.path.exists(file_path):
        return {
            "status": "error",
            "message": "File not found"
        }

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )


# ========================================
# GET STUDENT CERTIFICATES
# ========================================

@app.get("/student/{roll_number}/certificates")
async def get_student_certificates(roll_number: str):

    if not w3.is_connected():
        return {
            "status": "error",
            "message": "Blockchain connection failed"
        }

    student_ref_hash = hashlib.sha256(
        roll_number.encode()
    ).hexdigest()

    student_ref_bytes = bytes.fromhex(student_ref_hash)

    try:
        event_filter = contract.events.CertificateIssued.create_filter(
            from_block=0,
            to_block="latest"
        )

        events = event_filter.get_all_entries()

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch events: {str(e)}"
        }

    certificates = []

    for event in events:

        event_student_ref = event["args"]["studentRef"]

        if event_student_ref != student_ref_bytes:
            continue

        doc_hash = event["args"]["docHash"]

        result = contract.functions.verify(doc_hash).call()

        exists = result[0]
        valid = result[1]
        issuer = result[2]
        issuer_name = result[3]
        issued_at = result[4]
        revoked_at = result[5]
        ipfs_cid = result[6]
        ai_risk_score = result[7]

        if exists and valid:
            status = "AUTHENTIC"
        elif exists and not valid:
            status = "REVOKED"
        else:
            status = "UNKNOWN"

        doc_hash_hex = doc_hash.hex()

        verification_url = f"http://localhost:5173/verify/{doc_hash_hex}"

                # QR PDF URL banao
        qr_pdf_filename = f"certificate_with_qr_{doc_hash_hex[:16]}.pdf"
        qr_pdf_url = f"http://127.0.0.1:8000/download/{qr_pdf_filename}"

        certificates.append({
            "doc_hash": doc_hash_hex,
            "status": status,
            "issuer": issuer,
            "issuer_name": issuer_name,
            "issued_at": issued_at,
            "revoked_at": revoked_at,
            "ipfs_cid": ipfs_cid,
            "ai_risk_score": ai_risk_score,
            "verification_url": verification_url,
            "qr_pdf_url": qr_pdf_url
        })

    return {
        "status": "success",
        "roll_number": roll_number,
        "total": len(certificates),
        "certificates": certificates
    }
    # ========================================
# REVOKE CERTIFICATE
# ========================================

@app.post("/revoke")
async def revoke_certificate(
    doc_hash: str = Form(...),
    reason: str = Form(...)
):

    if not w3.is_connected():
        return {
            "status": "error",
            "message": "Blockchain connection failed"
        }

    # ------------------------------------
    # Validate hash
    # ------------------------------------

    if len(doc_hash) != 64:
        return {
            "status": "error",
            "message": "Invalid SHA-256 hash (must be 64 characters)"
        }

    try:
        doc_hash_bytes = bytes.fromhex(doc_hash)
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid hash format"
        }

    # ------------------------------------
    # Check if certificate exists
    # ------------------------------------

    existing = contract.functions.verify(doc_hash_bytes).call()

    if not existing[0]:
        return {
            "status": "error",
            "message": "Certificate not found on blockchain"
        }

    if existing[5] != 0:  # revokedAt
        return {
            "status": "error",
            "message": "Certificate is already revoked"
        }

    # ------------------------------------
    # Revoke on blockchain
    # ------------------------------------

    try:
        from backend.blockchain.revoke_certificate import revoke_certificate_on_chain

        tx_hash = revoke_certificate_on_chain(
            doc_hash_hex=doc_hash,
            reason=reason
        )

    except Exception as e:
        return {
            "status": "error",
            "message": f"Blockchain revoke failed: {str(e)}"
        }

    # ------------------------------------
    # Success
    # ------------------------------------

    return {
        "status": "success",
        "message": "Certificate revoked successfully",
        "doc_hash": doc_hash,
        "reason": reason,
        "tx_hash": tx_hash
    }