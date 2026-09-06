"""
Phase 2 — Script 2: RAG Search & Retrieval Engine
Queries Offline Vector Store with user questions and returns top matching legal chunks with citations.
"""

import os
import sys
import pickle
from typing import List, Dict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_DIR = os.path.join(PROJECT_ROOT, "data", "vectorstore")

def pf(msg):
    print(msg, flush=True)

def query_legal_database(query_text: str, top_k: int = 3) -> List[Dict]:
    """Queries Vector DB and returns top matching legal passages with citations."""
    offline_db_path = os.path.join(DB_DIR, "offline_vectorstore.pkl")

    if os.path.exists(offline_db_path):
        from sklearn.metrics.pairwise import cosine_similarity
        with open(offline_db_path, "rb") as f:
            data = pickle.load(f)

        chunks = data["chunks"]
        vectorizer = data["vectorizer"]
        matrix = data["matrix"]

        query_vec = vectorizer.transform([query_text])
        similarities = cosine_similarity(query_vec, matrix).flatten()
        top_indices = similarities.argsort()[::-1][:top_k]

        retrieved = []
        for idx in top_indices:
            item = chunks[idx]
            retrieved.append({
                "chunk_id": item.get("chunk_id", ""),
                "document_title": item.get("document_title", ""),
                "section": item.get("section", ""),
                "page": item.get("page", item.get("page_number")),
                "jurisdiction": item.get("jurisdiction", "India"),
                "authority": item.get("authority", ""),
                "content": item.get("content", ""),
                "relevance_score": round(float(similarities[idx]), 4)
            })
        return retrieved

    pf("[ERROR] No Vector Database found. Please run: python scripts/vector_store.py first.")
    return []

if __name__ == "__main__":
    test_query = sys.argv[1] if len(sys.argv) > 1 else "Can I patent traditional Ayurvedic knowledge under Section 3(p)?"
    pf(f"\n[SEARCH] Querying Database for: '{test_query}'\n" + "-"*55)
    
    results = query_legal_database(test_query, top_k=3)
    if not results:
        pf("No matches found or database not initialized.")
    for i, res in enumerate(results, 1):
        pf(f"\n[{i}] Source: {res['document_title']} | Section: {res['section']}")
        pf(f"    Authority: {res['authority']} ({res['jurisdiction']})")
        pf(f"    Relevance Score: {res['relevance_score']}")
        pf(f"    Passage: {res['content'][:250]}...")
