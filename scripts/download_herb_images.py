"""Download catalog images into a local cache for offline-friendly deployments."""

import os
import re
import urllib.request

from rag_assistant import HERBAL_KNOWLEDGE_BASE

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(PROJECT_ROOT, "assets", "herbs")

def safe_filename(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") + ".jpg"

def download_images() -> None:
    os.makedirs(IMAGE_DIR, exist_ok=True)
    for herb_key, herb in HERBAL_KNOWLEDGE_BASE.items():
        target = os.path.join(IMAGE_DIR, safe_filename(herb_key))
        if os.path.exists(target):
            continue
        try:
            request = urllib.request.Request(
                herb["image_url"],
                headers={"User-Agent": "IP-SAKTI-Sahayak/1.0 (local herb image cache)"}
            )
            with urllib.request.urlopen(request, timeout=30) as response, open(target, "wb") as image_file:
                image_file.write(response.read())
            print(f"[OK] {herb_key} -> {target}")
        except Exception as error:
            print(f"[WARN] Could not cache {herb_key}: {error}")

if __name__ == "__main__":
    download_images()