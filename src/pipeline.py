"""
pipeline.py

End-to-end pipeline:
  1. Detect + encode the face(s) in an input image
  2. Reverse-image-search the web for real matching pages (incl. social media)
  3. Build a tamper-evident record and anchor it on an EVM testnet
     (optionally pinning the full record to IPFS first)

Usage:
    python pipeline.py --image path/to/photo.jpg

See README.md for required environment variables and setup.
"""
import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from face_encode import load_and_encode, NoFaceFoundError, MultipleFacesError
from reverse_search import reverse_image_search
from ipfs_upload import pin_to_ipfs
from blockchain_logger import anchor_hash_on_chain

load_dotenv()

RECORDS_DIR = Path(__file__).resolve().parent.parent / "records"
RECORDS_DIR.mkdir(exist_ok=True)


def require_consent(image_path: str) -> None:
    """
    This tool is for checking where a photo you own or have consent for
    already appears online (e.g. catfishing / impersonation / stolen-photo
    detection), not for identifying people from photos you found of them.
    It writes its finding to a public blockchain permanently, so it
    refuses to run silently.
    """
    print(
        "\nThis tool looks up where a photo appears publicly online and "
        "permanently records that finding on a public blockchain.\n"
        f"Image: {image_path}\n"
    )
    answer = input(
        "Confirm this is a photo of yourself, or one you have the "
        "depicted person's explicit consent to look up (yes/no): "
    ).strip().lower()
    if answer not in ("y", "yes"):
        print("Consent not confirmed. Exiting without processing the image.")
        sys.exit(1)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(image_path: str, allow_multiple: bool, skip_consent: bool) -> dict:
    if not skip_consent:
        require_consent(image_path)

    image_bytes = Path(image_path).read_bytes()
    source_image_hash = sha256_hex(image_bytes)

    faces = load_and_encode(image_path, allow_multiple=allow_multiple)
    print(f"Detected {len(faces)} face(s).")
    encoding_hashes = [sha256_hex(f["encoding"].tobytes()) for f in faces]

    print("Running reverse image search (Google Cloud Vision Web Detection)...")
    search_results = reverse_image_search(image_path)

    if not search_results["social_media_matches"] and not search_results["full_matching_image_urls"]:
        print(
            "No confident matches found. Recording the null result anyway "
            "-- proving an image was NOT found publicly as of this date "
            "is itself sometimes useful evidence."
        )

    record = {
        "record_id": str(uuid.uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_image_sha256": source_image_hash,
        "face_encoding_sha256": encoding_hashes,
        "num_faces_detected": len(faces),
        "social_media_matches": search_results["social_media_matches"],
        "full_matching_image_urls": search_results["full_matching_image_urls"],
        "visually_similar_image_urls": search_results["visually_similar_image_urls"],
        "vision_best_guess_labels": search_results["best_guess_labels"],
    }

    record_path = RECORDS_DIR / f"{record['record_id']}.json"
    record_path.write_text(json.dumps(record, indent=2))
    print(f"Full record written to {record_path}")

    cid = pin_to_ipfs(record)
    if cid:
        record["ipfs_cid"] = cid
        anchor_payload = cid.encode("utf-8").hex()
        print(f"Record pinned to IPFS: {cid}")
    else:
        record_hash = sha256_hex(json.dumps(record, sort_keys=True).encode("utf-8"))
        record["record_sha256"] = record_hash
        anchor_payload = record_hash

    record_path.write_text(json.dumps(record, indent=2))

    print("Anchoring record on-chain...")
    chain_result = anchor_hash_on_chain(anchor_payload)
    record["blockchain_anchor"] = chain_result
    record_path.write_text(json.dumps(record, indent=2))

    print("\nDone.")
    print(f"Transaction hash: {chain_result['tx_hash']}")
    print(chain_result["explorer_hint"])
    print(f"Local record: {record_path}")

    return record


def main():
    parser = argparse.ArgumentParser(description="Photo-reuse detection + blockchain notarization pipeline")
    parser.add_argument("--image", required=True, help="Path to the input photo")
    parser.add_argument("--allow-multiple", action="store_true", help="Process all faces if more than one is found")
    parser.add_argument("--skip-consent-prompt", action="store_true", help="For automated/CI test runs only")
    args = parser.parse_args()

    try:
        run(args.image, args.allow_multiple, args.skip_consent_prompt)
    except (NoFaceFoundError, MultipleFacesError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
