"""
Phase 1 — Script 2: Section-Aware Chunking & Metadata Enrichment Pipeline
Splits legal documents into complete legal clauses and attaches rich metadata.
"""

import os
import json
import re
from typing import List, Dict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "chunks.json")

def parse_sections(filename: str, content: str) -> List[Dict]:
    """
    Parses document into distinct legal sections using regex pattern matching.
    Attaches metadata: document_title, section, jurisdiction, authority, topic.
    """
    chunks = []
    
    # Simple regex to split by legal clause numbers like (a), (b), (p), Rule 158B, etc.
    # Split content by line blocks
    lines = content.split("\n")
    current_doc_title = filename
    current_section = "General Provision"
    current_text_buffer = []

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        
        # Check if line indicates document header or section header
        if line_str.startswith("# SECTION") or line_str.startswith("# DRUGS"):
            current_doc_title = line_str.replace("#", "").strip()
            continue
        
        # Match legal clauses like (a), (b), (p), Rule 158B, etc.
        clause_match = re.match(r'^(\([a-z0-9]+\)|Rule\s+[0-9]+[A-Z]*|3\.)\s*(.*)', line_str)
        if clause_match:
            # Flush previous chunk
            if current_text_buffer:
                chunks.append({
                    "chunk_id": f"{filename}_chunk_{len(chunks)+1}",
                    "document_title": current_doc_title,
                    "section": current_section,
                    "jurisdiction": "India",
                    "authority": "Indian Patent Office / Ministry of AYUSH",
                    "content": "\n".join(current_text_buffer).strip()
                })
                current_text_buffer = []
            
            current_section = clause_match.group(1)
            current_text_buffer.append(line_str)
        else:
            current_text_buffer.append(line_str)

    # Flush final chunk
    if current_text_buffer:
        chunks.append({
            "chunk_id": f"{filename}_chunk_{len(chunks)+1}",
            "document_title": current_doc_title,
            "section": current_section,
            "jurisdiction": "India",
            "authority": "Indian Patent Office / Ministry of AYUSH",
            "content": "\n".join(current_text_buffer).strip()
        })

    return chunks

def run_chunking_pipeline():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    all_chunks = []

    if not os.path.exists(RAW_DIR):
        print(f"Directory {RAW_DIR} does not exist. Please place text/PDF files in {RAW_DIR}.")
        return

    for fname in os.listdir(RAW_DIR):
        if fname.endswith(".txt") or fname.endswith(".md"):
            fpath = os.path.join(RAW_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    raw_content = f.read()
            except UnicodeDecodeError:
                with open(fpath, "r", encoding="latin-1", errors="ignore") as f:
                    raw_content = f.read()
            
            chunks = parse_sections(fname, raw_content)
            all_chunks.extend(chunks)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        json.dump(all_chunks, out_f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Chunking Complete! Processed {len(all_chunks)} legal chunks.")
    print(f"[OUTPUT] Output saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_chunking_pipeline()
