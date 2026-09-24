import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")

CONTRACT_ADDRESS = os.getenv(
    "CONTRACT_ADDRESS",
    "0x5fbdb2315678afecb367f032d93f642f64180aa3"
)

INSTITUTION_PRIVATE_KEY = os.getenv("INSTITUTION_PRIVATE_KEY")


with open(
    "backend/blockchain/contract_abi.json",
    "r",
    encoding="utf-8"
) as f:
    CONTRACT_ABI = json.load(f)


def revoke_certificate_on_chain(doc_hash_hex: str, reason: str) -> str:
    """
    Calls revokeCertificate() on smart contract.
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

    account = w3.eth.account.from_key(INSTITUTION_PRIVATE_KEY)

    doc_hash_bytes = bytes.fromhex(doc_hash_hex)

    nonce = w3.eth.get_transaction_count(account.address)

    tx = contract.functions.revokeCertificate(
        doc_hash_bytes,
        reason
    ).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 300000,
        "gasPrice": w3.eth.gas_price,
        "chainId": w3.eth.chain_id
    })

    signed_tx = w3.eth.account.sign_transaction(
        tx,
        private_key=INSTITUTION_PRIVATE_KEY
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed_tx.raw_transaction
    )

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash,
        timeout=120
    )

    if receipt.status != 1:
        raise Exception("Transaction failed on-chain")

    return tx_hash.hex()