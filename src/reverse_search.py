"""
reverse_search.py

Performs genuine reverse image search using Google Lens via SerpApi's direct Image API.
Formats results to match every key expected by pipeline.py.
"""
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from the project root
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

SOCIAL_DOMAINS = [
    "instagram.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "tiktok.com",
    "reddit.com",
    "pinterest.com",
    "youtube.com",
    "t.me"
]

def reverse_image_search(image_path: str):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY is missing in your .env file")

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    print("Uploading image directly to SerpApi for Google Lens...")
    with open(path, "rb") as f:
        upload_resp = requests.post(
            "https://serpapi.com/image",
            files={"image": f},
            data={"api_key": api_key}
        )

    upload_data = upload_resp.json()
    if "image_id" not in upload_data:
        raise RuntimeError(f"SerpApi upload failed: {upload_data.get('error', upload_data)}")

    image_id = upload_data["image_id"]

    print("Searching Google Lens index via SerpApi...")
    params = {
        "engine": "google_lens",
        "image_id": image_id,
        "api_key": api_key
    }

    response = requests.get("https://serpapi.com/search", params=params)
    results = response.json()

    visual_matches = results.get("visual_matches", [])

    pages_with_matching_images = []
    full_matching_image_urls = []
    visually_similar_image_urls = []
    social_media_matches = []
    all_web_matches = []
    best_guess_labels = []

    for match in visual_matches:
        page_url = match.get("link")
        thumbnail = match.get("thumbnail")
        title = match.get("title", "")
        source = match.get("source", "")

        if page_url:
            entry = {"url": page_url, "title": title, "source": source, "page_title": title}
            pages_with_matching_images.append(entry)
            all_web_matches.append(entry)
            
            if any(domain in page_url.lower() for domain in SOCIAL_DOMAINS):
                social_media_matches.append(entry)

        if thumbnail:
            visually_similar_image_urls.append(thumbnail)
            if not full_matching_image_urls:
                full_matching_image_urls.append(thumbnail)

    # Extract knowledge graph / entity hints if present
    web_entities = []
    kg = results.get("knowledge_graph", [])
    if isinstance(kg, list):
        for item in kg:
            if isinstance(item, dict) and "title" in item:
                web_entities.append({"description": item["title"], "score": 1.0})
                best_guess_labels.append(item["title"])
    elif isinstance(kg, dict) and "title" in kg:
        web_entities.append({"description": kg["title"], "score": 1.0})
        best_guess_labels.append(kg["title"])

    # Fallback to visual match titles if no KG label exists
    if not best_guess_labels and visual_matches:
        first_title = visual_matches[0].get("title")
        if first_title:
            best_guess_labels.append(first_title)

    return {
        "social_media_matches": social_media_matches,
        "all_web_matches": all_web_matches[:10],
        "total_matches_found": len(all_web_matches),
        "full_matching_image_urls": full_matching_image_urls,
        "partial_matching_image_urls": [],
        "pages_with_matching_images": pages_with_matching_images,
        "visually_similar_image_urls": visually_similar_image_urls,
        "web_entities": web_entities,
        "best_guess_labels": best_guess_labels
    }