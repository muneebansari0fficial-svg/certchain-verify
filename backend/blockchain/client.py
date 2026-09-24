from web3 import Web3

# Local Hardhat blockchain
RPC_URL = "http://127.0.0.1:8545"

# Deployed CertificateRegistry contract
CONTRACT_ADDRESS = "0x5fbdb2315678afecb367f032d93f642f64180aa3"

# Connect to Hardhat
w3 = Web3(Web3.HTTPProvider(RPC_URL))


def is_connected():
    return w3.is_connected()


def get_block_number():
    return w3.eth.block_number
