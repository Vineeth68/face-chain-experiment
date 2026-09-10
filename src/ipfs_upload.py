"""
ipfs_upload.py

Optional: pins the full match record to IPFS (via web3.storage) so the
on-chain anchor can point to retrievable, content-addressed data
rather than just a bare hash. If no WEB3_STORAGE_TOKEN is configured,
the pipeline falls back to anchoring a plain SHA-256 hash of the
record instead -- still tamper-evident, just not independently
retrievable from the chain alone.
"""
import json
import os
from typing import Optional

import requests

WEB3_STORAGE_ENDPOINT = "https://api.web3.storage/upload"


def pin_to_ipfs(record: dict) -> Optional[str]:
    token = os.environ.get("WEB3_STORAGE_TOKEN")
    if not token:
        return None

    payload = json.dumps(record, sort_keys=True).encode("utf-8")
    resp = requests.post(
        WEB3_STORAGE_ENDPOINT,
        headers={"Authorization": f"Bearer {token}"},
        data=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["cid"]
