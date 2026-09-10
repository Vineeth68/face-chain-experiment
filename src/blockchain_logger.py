"""
blockchain_logger.py

Anchors a tamper-evident payload (a hash, or an IPFS CID) on an
EVM-compatible testnet by embedding it in the `data` field of a
zero-value transaction sent from your wallet to itself.

This is a minimal, contract-free notarization pattern (the same idea
used by services like OpenTimestamps / "proof of existence"): once the
transaction is mined, its calldata is permanently part of the chain's
history. Reproducing the record and re-hashing it will only match the
on-chain value if nothing was altered, and the timestamp of the block
proves *when* the record existed in this form.

Default network: Polygon Amoy testnet (see README for why).
"""
import os

from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from the project root
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

def anchor_hash_on_chain(hex_payload: str) -> dict:
    rpc_url = os.environ["RPC_URL"]
    private_key = os.environ["PRIVATE_KEY"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Could not connect to RPC endpoint: {rpc_url}")

    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    clean_hex = hex_payload[2:] if hex_payload.startswith("0x") else hex_payload
    data_bytes = bytes.fromhex(clean_hex)

    tx = {
        "nonce": nonce,
        "to": account.address,   # self-send; only the calldata matters
        "value": 0,
        "gas": 100_000,
        "gasPrice": w3.eth.gas_price,
        "data": data_bytes,
        "chainId": w3.eth.chain_id,
    }

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return {
        "tx_hash": tx_hash.hex(),
        "block_number": receipt.blockNumber,
        "chain_id": w3.eth.chain_id,
        "explorer_hint": (
            "Look up the tx_hash on your network's block explorer, e.g. "
            "https://amoy.polygonscan.com/tx/<tx_hash> for Polygon Amoy, "
            "or https://sepolia.etherscan.io/tx/<tx_hash> for Ethereum Sepolia."
        ),
    }
