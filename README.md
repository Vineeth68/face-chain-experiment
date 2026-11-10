# face-verify-chain

A lightweight pipeline to detect facial embeddings, query public reverse-image search indexes, and anchor cryptographic provenance proofs on EVM testnets (Polygon Amoy).

Built to audit unauthorized photo re-use and establish proof-of-existence without exposing raw biometrics on-chain.

---

## Overview

1. **Detection & Encoding:** Extracts 128-d face descriptors using `dlib` / `face_recognition`.
2. **Web Index Lookup:** Queries reverse-image search via SerpApi (Google Lens engine) to aggregate matched URLs across public web and social platforms.
3. **Integrity Packaging:** Generates a structured JSON record containing image hashes, metadata, and matched sources.
4. **On-Chain Notarization:** Hashes the record (SHA-256) and logs it into transaction calldata on Polygon Amoy via `web3.py`.


## Tech Stack

* **Python 3.10+**
* **dlib / face_recognition** (HOG + Deep Metric Face Embeddings)
* **SerpApi** (Google Lens visual search endpoint)
* **Web3.py** (EVM transaction signing & RPC interaction)
* **Polygon Amoy Testnet** (EVM-compatible ledger)

---


Technical Notes & Limitations
Visual Matching vs. Biometric Search: Google Lens matches image visual similarity, page context, and near-duplicates across public web indexes; it is not a direct facial recognition vector database.

On-Chain Privacy: Raw image bytes and biometric vectors remain strictly local. Only deterministic SHA-256 digests are broadcast on-chain.

Network Target: Defaults to Polygon Amoy testnet. The RPC provider and contract calldata target can be swapped for any EVM-compatible chain via .env.
