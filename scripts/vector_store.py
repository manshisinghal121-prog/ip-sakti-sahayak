"""
Phase 1 & 2 Vector Store Builder
Fast Offline Vector Database for IP-SAKTI Sahayak (Zero Internet Required)
"""

import os
import json
import pickle
from typing import List, Dict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CHUNKS_FILE = os.path.join(PROJECT_ROOT, "data", "processed", "chunks.json")
DB_DIR = os.path.join(PROJECT_ROOT, "data", "vectorstore")

def print_flush(msg):
    print(msg, flush=True)

def build_vector_database():
    if not os.path.exists(CHUNKS_FILE):
        print_flush(f"Error: {CHUNKS_FILE} not found. Please run Phase 1 chunking pipeline first.")
        return

    print_flush("Loading processed legal chunks...")
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print_flush(f"Loaded {len(chunks)} chunks. Building Vector Database (Offline Engine)...")
    os.makedirs(DB_DIR, exist_ok=True)

    documents = [item["content"] for item in chunks]

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError:
        print_flush("Installing scikit-learn for offline vectorization...")
        os.system("pip install scikit-learn")
        from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(documents)

    offline_db_path = os.path.join(DB_DIR, "offline_vectorstore.pkl")
    with open(offline_db_path, "wb") as f:
        pickle.dump({
            "chunks": chunks,
            "vectorizer": vectorizer,
            "matrix": tfidf_matrix
        }, f)

    print_flush(f"[SUCCESS] Vector Store Built Successfully! Saved 18 vector representations to {offline_db_path}")

if __name__ == "__main__":
    build_vector_database()
