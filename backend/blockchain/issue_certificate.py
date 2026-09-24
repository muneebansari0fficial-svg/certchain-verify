import os
import json
from web3 import Web3
from dotenv import load_dotenv

from pathlib import Path

# backend/.env ka absolute path
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")

CONTRACT_ADDRESS = os.getenv(
    "CONTRACT_ADDRESS",
    "0x5fbdb2315678afecb367f032d93f642f64180aa3"
)

INSTITUTION_PRIVATE_KEY = os.getenv("INSTITUTION_PRIVATE_KEY")


# Load contract ABI
with open(
    "backend/blockchain/contract_abi.json",
    "r",
    encoding="utf-8"
) as f:
    CONTRACT_ABI = json.load(f)


def issue_certificate_on_chain(
    doc_hash_hex: str,
    student_ref_hex: str,
    ipfs_cid: str,
    ai_risk_score: int
) -> str:
    """
    Calls issueCertificate() on smart contract.
    Returns transaction hash.
    """

    if not INSTITUTION_PRIVATE_KEY:
        raise Exception("INSTITUTION_PRIVATE_KEY missing in .env")

    w3 = Web3(Web3.HTTPProvider(RPC_URL))

    if not w3.is_connected():
        raise Exception("Blockchain connection failed")

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=CONTRACT_ABI
    )

    # Institution account
    institution_account = w3.eth.account.from_key(
        INSTITUTION_PRIVATE_KEY
    )

    # Convert doc hash to bytes32
    doc_hash_bytes = bytes.fromhex(doc_hash_hex)

    # Student ref: pad to 32 bytes if short
    if len(student_ref_hex) < 64:
        student_ref_hex = student_ref_hex.ljust(64, "0")

    student_ref_bytes = bytes.fromhex(student_ref_hex)

    # Build transaction
    nonce = w3.eth.get_transaction_count(
        institution_account.address
    )

    tx = contract.functions.issueCertificate(
        doc_hash_bytes,
        student_ref_bytes,
        ipfs_cid,
        ai_risk_score
    ).build_transaction({
        "from": institution_account.address,
        "nonce": nonce,
        "gas": 500000,
        "gasPrice": w3.eth.gas_price,
        "chainId": w3.eth.chain_id
    })

    # Sign
    signed_tx = w3.eth.account.sign_transaction(
        tx,
        private_key=INSTITUTION_PRIVATE_KEY
    )

    # Send
    tx_hash = w3.eth.send_raw_transaction(
        signed_tx.raw_transaction
    )

    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash,
        timeout=120
    )

    if receipt.status != 1:
        raise Exception("Transaction failed on-chain")

    return tx_hash.hex()