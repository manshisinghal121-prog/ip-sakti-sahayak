"""
Phase 1 — Script 1: Data Parser & Text Cleaner
Reads raw PDF/text regulatory documents from data/raw/ and extracts clean text blocks.
"""

import os
import re
from typing import List, Dict

RAW_DATA_DIR = os.path.join(os-[#1], "..", "data", "raw") if "__file__" in globals() else "data/raw"

def clean_text(text: str) -> str:
    """Removes extra whitespace, page numbers, and artifact headers."""
    # Remove multiple line breaks and normalize spaces
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def load_raw_text_files(directory: str) -> List[Dict[str, str]]:
    """Loads all .txt and .md files from directory."""
    documents = []
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist yet. Creating it...")
        os.makedirs(directory, exist_ok=True)
        return documents

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if filename.endswith(".txt") or filename.endswith(".md"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                cleaned = clean_text(content)
                documents.append({
                    "filename": filename,
                    "content": cleaned
                })
    return documents

if __name__ == "__main__":
    docs = load_raw_text_files("data/raw")
    print(f"Loaded {len(docs)} documents from data/raw/")
    for doc in docs:
        print(f" - {doc['filename']}: {len(doc['content'])} characters")
