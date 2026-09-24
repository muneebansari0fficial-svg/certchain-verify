import json
from web3 import Web3

RPC_URL = "http://127.0.0.1:8545"

CONTRACT_ADDRESS = "0x5fbdb2315678afecb367f032d93f642f64180aa3"

# Load ABI
with open(
    "backend/blockchain/contract_abi.json",
    "r",
    encoding="utf-8"
) as f:
    ABI = json.load(f)

# Connect to Hardhat
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise Exception("Blockchain connection failed")

# Create contract object
contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=ABI
)


# Certificate SHA-256 hash
doc_hash = "0x138683f118900e721414a813fd991a56374037012b23182db6d53a6d474304f3"


# Call blockchain verify()
result = contract.functions.verify(
    bytes.fromhex(doc_hash[2:])
).call()


print("================================")
print("BLOCKCHAIN VERIFICATION")
print("================================")

print("Exists:", result[0])
print("Valid:", result[1])
print("Issuer:", result[2])
print("Issuer Name:", result[3])
print("Issued At:", result[4])
print("Revoked At:", result[5])
print("IPFS CID:", result[6])
print("AI Risk Score:", result[7])

print("================================")

if result[0] and result[1]:
    print("RESULT: CERTIFICATE IS AUTHENTIC")
elif result[0] and not result[1]:
    print("RESULT: CERTIFICATE IS REVOKED / INVALID")
else:
    print("RESULT: CERTIFICATE NOT REGISTERED")

