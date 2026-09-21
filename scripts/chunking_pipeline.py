"""
IP-SAKTI — Production Chunking & Metadata Enrichment Pipeline

Splits legal/knowledge documents into context-preserving chunks and attaches
source-aware metadata for reliable RAG retrieval and citations.
"""

import os
import json
import re
from typing import List, Dict, Tuple

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "chunks.json")

# Keep very small legal clauses with surrounding context instead of creating
# isolated fragments that are hard for retrieval to interpret.
MIN_CHUNK_CHARS = 220
MAX_CHUNK_CHARS = 2400


def load_source_content(filepath: str) -> str:
    """Read text/markdown or extract text from PDF bytes."""
    with open(filepath, "rb") as source_file:
        raw_bytes = source_file.read()

    if raw_bytes.startswith(b"%PDF") and PdfReader is not None:
        return "\f".join(page.extract_text() or "" for page in PdfReader(filepath).pages)

    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return raw_bytes.decode("latin-1", errors="ignore")


def _normalise_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def detect_source_metadata(filename: str, document_title: str, content: str) -> Tuple[str, str, str]:
    """
    Infer source metadata at document level.

    Priority is given to explicit document/title signals, then content signals.
    This prevents every document from incorrectly receiving the same authority.
    """
    haystack = _normalise_name(" ".join([filename, document_title, content[:6000]]))

    rules = [
        ("Biodiversity", "National Biodiversity Authority (NBA)", "Biodiversity_ABS", [
            "biological diversity act", "biodiversity act", "national biodiversity authority",
            "biological resources", "access and benefit sharing", "benefit sharing"
        ]),
        ("Patent", "Indian Patent Office / Office of the Controller General of Patents", "Patentability", [
            "patents act", "patent office", "controller general of patents", "patent rules",
            "intellectual property office", "patentability"
        ]),
        ("AYUSH", "Ministry of AYUSH, Government of India", "AYUSH_Licensing", [
            "ministry of ayush", "ayush", "rule 158b", "schedule t", "drugs and cosmetics",
            "ayurvedic siddha unani", "asu drugs"
        ]),
        ("WIPO", "World Intellectual Property Organization (WIPO)", "WIPO_Guidance", [
            "world intellectual property organization", "wipo", "genetic resources and associated traditional knowledge"
        ]),
        ("WHO", "World Health Organization (WHO)", "WHO_Guidance", [
            "world health organization", "who traditional medicine", "who guidelines"
        ]),
        ("Traditional Knowledge", "Traditional Knowledge Digital Library (TKDL) / Traditional Knowledge sources", "Traditional_Knowledge", [
            "traditional knowledge digital library", "tkdl", "traditional knowledge"
        ]),
    ]

    for label, authority, topic, keywords in rules:
        if any(keyword in haystack for keyword in keywords):
            return authority, topic, label

    return "Source authority not explicitly identified", "General", "Other"


def detect_knowledge_source(text: str, document_source: str) -> str:
    """Classify the knowledge source without letting incidental words dominate."""
    lowered = text.lower()

    if document_source == "WIPO" or "world intellectual property organization" in lowered:
        return "WIPO"
    if document_source == "WHO" or "world health organization" in lowered:
        return "WHO"
    if document_source == "Traditional Knowledge" or "traditional knowledge digital library" in lowered:
        return "Traditional"
    if "traditional knowledge" in lowered and len(re.findall(r"\btraditional knowledge\b", lowered)) >= 1:
        return "Traditional"
    if document_source in {"Biodiversity", "Patent", "AYUSH"}:
        return "Legal/Regulatory"
    return "Other"


def _is_clause_start(line: str) -> bool:
    """Detect common top-level legal clause/section markers."""
    patterns = [
        r"^\(?\d{1,3}\)?[\.)]\s+",             # 1. / 1) / (1)
        r"^\([a-z]\)\s+",                       # (a)
        r"^[a-z][\.)]\s+",                      # a. / a)
        r"^Rule\s+\d+[A-Z]*\b",                 # Rule 158B
        r"^Section\s+\d+[A-Z]*\b",              # Section 3
        r"^Article\s+\d+[A-Z]*\b",              # Article 12
        r"^\d+\.\d+(?:\.\d+)*\s+",            # 3.1 / 3.1.2
    ]
    return any(re.match(pattern, line, flags=re.IGNORECASE) for pattern in patterns)


def _flush_chunk(
    chunks: List[Dict],
    buffer: List[str],
    filename: str,
    document_title: str,
    section: str,
    page: int,
    authority: str,
    topic: str,
    document_source: str,
) -> None:
    text = "\n".join(buffer).strip()
    if not text:
        return

    chunks.append({
        "chunk_id": f"{filename}_chunk_{len(chunks) + 1}",
        "document_title": document_title,
        "section": section,
        "page": page,
        "jurisdiction": "India",
        "authority": authority,
        "topic": topic,
        "content": text,
        "knowledge_source": detect_knowledge_source(text, document_source),
    })


def _is_explicit_legal_clause(section: str) -> bool:
    """Return True for clause/Rule labels that should remain independently retrievable."""
    value = str(section or "").strip().lower()

    # Examples: (a), (p), (1), Rule 158B, Section 3(p), Article 2.
    return bool(
        re.match(r"^\([a-z0-9]+\)", value)
        or re.match(r"^rule\s+\d+[a-z]*", value)
        or re.match(r"^section\s+\d+", value)
        or re.match(r"^article\s+\d+", value)
    )


def _merge_small_chunks(chunks: List[Dict]) -> List[Dict]:
    """
    Merge only genuinely tiny continuation fragments.

    Explicit legal clauses are NEVER merged with neighboring clauses.
    This is important for precise retrieval of provisions such as Section
    3(p) of the Patents Act.
    """
    if not chunks:
        return []

    merged: List[Dict] = []

    for chunk in chunks:
        can_merge = (
            merged
            and len(chunk["content"]) < MIN_CHUNK_CHARS
            and merged[-1]["document_title"] == chunk["document_title"]
            and merged[-1]["topic"] == chunk["topic"]
            and not _is_explicit_legal_clause(chunk.get("section", ""))
            and not _is_explicit_legal_clause(merged[-1].get("section", ""))
        )

        if can_merge:
            merged[-1]["content"] = (
                merged[-1]["content"] + "\n" + chunk["content"]
            ).strip()
            merged[-1]["section"] = (
                f'{merged[-1]["section"]} → {chunk["section"]}'
            )
            continue

        merged.append(dict(chunk))

    # Do not merge a final explicit legal clause into its predecessor.
    # Preserve its exact section label even when it is short.
    for index, chunk in enumerate(merged, start=1):
        chunk["chunk_id"] = (
            f'{chunk["chunk_id"].split("_chunk_")[0]}_chunk_{index}'
        )

    return merged


def parse_sections(filename: str, content: str) -> List[Dict]:
    """Parse a source into context-preserving, source-aware legal chunks."""
    lines = content.split("\n")
    current_doc_title = os.path.splitext(filename)[0]
    current_section = "General Provision"
    current_text_buffer: List[str] = []
    current_page = 1
    chunk_start_page = 1

    authority, topic, document_source = detect_source_metadata(filename, current_doc_title, content)
    chunks: List[Dict] = []

    for line in lines:
        page_breaks = line.count("\f")
        if page_breaks:
            current_page += page_breaks

        line_str = re.sub(r"\s+", " ", line.replace("\f", " ")).strip()
        if not line_str:
            continue

        # Markdown-style source/document headers.
        if line_str.startswith("# SECTION") or line_str.startswith("# DRUGS"):
            current_doc_title = line_str.replace("#", "").strip()
            authority, topic, document_source = detect_source_metadata(
                filename, current_doc_title, content
            )
            continue

        if _is_clause_start(line_str):
            # Only flush if the current buffer is meaningful. Tiny fragments
            # are merged later so they do not become standalone RAG evidence.
            if current_text_buffer:
                _flush_chunk(
                    chunks, current_text_buffer, filename, current_doc_title,
                    current_section, chunk_start_page, authority, topic, document_source
                )
                current_text_buffer = []

            marker_match = re.match(
                r"^(\(?\d{1,3}\)?[\.)]|\([a-z]\)|[a-z][\.)]|Rule\s+\d+[A-Z]*|Section\s+\d+[A-Z]*|Article\s+\d+[A-Z]*|\d+\.\d+(?:\.\d+)*)",
                line_str,
                flags=re.IGNORECASE,
            )
            current_section = marker_match.group(1) if marker_match else "Legal Provision"
            chunk_start_page = current_page
            current_text_buffer.append(line_str)
        else:
            current_text_buffer.append(line_str)

    if current_text_buffer:
        _flush_chunk(
            chunks, current_text_buffer, filename, current_doc_title,
            current_section, chunk_start_page, authority, topic, document_source
        )

    chunks = _merge_small_chunks(chunks)

    # Split unusually large chunks at sentence boundaries rather than making
    # retrieval operate on a huge legal passage.
    final_chunks: List[Dict] = []
    for chunk in chunks:
        text = chunk["content"]
        if len(text) <= MAX_CHUNK_CHARS:
            final_chunks.append(chunk)
            continue

        sentences = re.split(r"(?<=[.!?])\s+", text)
        buffer = ""
        part = 1
        for sentence in sentences:
            if buffer and len(buffer) + len(sentence) + 1 > MAX_CHUNK_CHARS:
                new_chunk = dict(chunk)
                new_chunk["content"] = buffer.strip()
                new_chunk["section"] = f'{chunk["section"]} (part {part})'
                final_chunks.append(new_chunk)
                part += 1
                buffer = sentence
            else:
                buffer = f"{buffer} {sentence}".strip()
        if buffer:
            new_chunk = dict(chunk)
            new_chunk["content"] = buffer.strip()
            new_chunk["section"] = f'{chunk["section"]} (part {part})' if part > 1 else chunk["section"]
            final_chunks.append(new_chunk)

    for index, chunk in enumerate(final_chunks, start=1):
        chunk["chunk_id"] = f"{filename}_chunk_{index}"

    return final_chunks


def run_chunking_pipeline() -> None:
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    all_chunks: List[Dict] = []

    if not os.path.exists(RAW_DIR):
        print(f"[ERROR] Directory {RAW_DIR} does not exist. Place source files there first.")
        return

    for fname in sorted(os.listdir(RAW_DIR)):
        if not (fname.endswith(".txt") or fname.endswith(".md") or fname.endswith(".pdf")):
            continue

        fpath = os.path.join(RAW_DIR, fname)
        raw_content = load_source_content(fpath)
        chunks = parse_sections(fname, raw_content)
        all_chunks.extend(chunks)
        print(f"[SOURCE] {fname}: {len(chunks)} chunks")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        json.dump(all_chunks, out_f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Chunking complete. Processed {len(all_chunks)} chunks.")
    print(f"[OUTPUT] {OUTPUT_FILE}")


if __name__ == "__main__":
    run_chunking_pipeline()
