"""
Phase 2 — Script 2: Production Hybrid RAG Retrieval Engine

Retrieves legal knowledge from the offline TF-IDF vector store using:
1. Lexical similarity (TF-IDF cosine similarity)
2. Topic matching from chunk metadata
3. Authority/source matching
4. Lightweight query-term overlap

This keeps the existing offline vector store compatible while making
retrieval more aware of the legal knowledge-base metadata.
"""

import os
import sys
import pickle
import re
from typing import List, Dict, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_DIR = os.path.join(PROJECT_ROOT, "data", "vectorstore")


# ---------------------------------------------------------------------------
# Query intent/topic routing
# ---------------------------------------------------------------------------

TOPIC_RULES: Dict[str, Tuple[str, ...]] = {
    "Patentability": (
        "patent", "patentability", "novelty", "prior art",
        "inventive step", "section 3", "section 3(p)", "ip rights",
        "intellectual property",
    ),
    "AYUSH_Licensing": (
        "ayush", "license", "licensing", "licence", "rule 158b",
        "158b", "schedule t", "gmp", "manufacturing",
    ),
    "Safety": (
        "safety", "safe", "dosage", "dose", "contraindication",
        "side effect", "interaction", "toxicity", "quality",
    ),
    "Biodiversity_ABS": (
        "biodiversity", "biological resource", "biological resources",
        "access and benefit sharing", "benefit sharing", "abs",
        "nba", "national biodiversity authority", "benefit-sharing",
    ),
    "Traditional_Knowledge": (
        "traditional knowledge", "traditional use", "traditional uses",
        "tkdl", "ayurvedic knowledge", "folk knowledge",
    ),
    "Regulatory_Compliance": (
        "regulatory compliance", "compliance", "regulation",
        "regulatory requirement", "requirements", "approval",
    ),
    "WIPO_Guidance": (
        "wipo", "world intellectual property organization",
        "genetic resources", "traditional knowledge policy",
    ),
    "WHO_Guidance": (
        "who", "world health organization", "traditional medicine",
        "herbal medicine", "botanical", "quality control",
    ),
}


AUTHORITY_RULES: Dict[str, Tuple[str, ...]] = {
    "National Biodiversity Authority (NBA)": (
        "biodiversity", "biological resource", "access and benefit sharing",
        "benefit sharing", "nba", "national biodiversity authority",
    ),
    "Indian Patent Office / Office of the Controller General of Patents": (
        "patent", "patentability", "prior art", "novelty",
        "inventive step", "section 3",
    ),
    "Ministry of AYUSH": (
        "ayush", "licensing", "rule 158b", "schedule t", "gmp",
    ),
    "World Health Organization (WHO)": (
        "who", "world health organization", "traditional medicine",
    ),
    "World Intellectual Property Organization (WIPO)": (
        "wipo", "world intellectual property organization",
        "genetic resources",
    ),
}


def pf(msg: str) -> None:
    print(msg, flush=True)


def _normalise(text: str) -> str:
    """Normalise text for lightweight metadata matching."""
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def _matched_topics(query: str) -> List[str]:
    """Return knowledge-base topics whose routing terms occur in the query."""
    q = _normalise(query)
    matches = []

    for topic, terms in TOPIC_RULES.items():
        if any(term in q for term in terms):
            matches.append(topic)

    return matches


def _matched_authorities(query: str) -> List[str]:
    """Return authorities whose routing terms occur in the query."""
    q = _normalise(query)
    matches = []

    for authority, terms in AUTHORITY_RULES.items():
        if any(term in q for term in terms):
            matches.append(authority)

    return matches


def _extract_legal_references(query: str) -> List[str]:
    """Extract exact legal references such as Section 3(p), Rule 158B."""
    q = _normalise(query)
    refs = []

    patterns = [
        r"section\s+\d+[a-z]?(?:\([a-z0-9]+\))?",
        r"rule\s+\d+[a-z]*",
        r"schedule\s+[a-z0-9]+",
    ]

    for pattern in patterns:
        refs.extend(re.findall(pattern, q))

    return list(dict.fromkeys(refs))


def _exact_reference_score(query: str, item: Dict) -> float:
    """
    Boost chunks that correspond to an exact legal reference.

    The source chunks often store Section 3(p) as:
      section = "(p)"
    while the surrounding document is patent_act_1970.txt.
    Therefore matching only the literal phrase "section 3(p)" in content
    would miss the correct legal clause.
    """
    references = _extract_legal_references(query)
    if not references:
        return 0.0

    section_field = _normalise(item.get("section", ""))
    document_title = _normalise(item.get("document_title", ""))
    content = _normalise(item.get("content", ""))

    score = 0.0

    for ref in references:
        # Direct textual match anywhere in the source metadata/content.
        if ref in " ".join([document_title, section_field, content]):
            score = max(score, 1.0)
            continue

        section_match = re.match(
            r"section\s+(\d+)(?:[a-z])?(?:\(([a-z0-9]+)\))?$",
            ref,
        )

        if section_match:
            section_number = section_match.group(1)
            subsection = section_match.group(2)

            # Patent Act chunks represent Section 3(p) as section "(p)".
            if (
                section_number == "3"
                and subsection
                and section_field == f"({subsection})"
                and "patent_act" in document_title
            ):
                score = max(score, 1.0)
                continue

            # A plain Section N can be supported by a section field/content
            # that explicitly contains that section number.
            if (
                not subsection
                and (
                    section_field == section_number
                    or f"section {section_number}" in content
                )
            ):
                score = max(score, 1.0)
                continue

        rule_match = re.match(r"rule\s+(\d+[a-z]*)$", ref)
        if rule_match:
            rule_number = rule_match.group(1)
            if (
                f"rule {rule_number}" in document_title
                or section_field == f"rule {rule_number}"
                or f"rule {rule_number}" in content
            ):
                score = max(score, 1.0)
                continue

        schedule_match = re.match(r"schedule\s+([a-z0-9]+)$", ref)
        if schedule_match:
            schedule_name = schedule_match.group(1)
            if f"schedule {schedule_name}" in " ".join(
                [document_title, section_field, content]
            ):
                score = max(score, 1.0)

    return score


def _metadata_score(
    query: str,
    item: Dict,
    matched_topics: List[str],
    matched_authorities: List[str],
) -> float:
    """
    Calculate a small metadata-aware boost.

    Topic is the strongest metadata signal, followed by authority and
    document-title/section keyword overlap.
    """
    score = 0.0

    item_topic = str(item.get("topic", "") or "")
    item_authority = str(item.get("authority", "") or "")
    document_text = " ".join(
        [
            str(item.get("document_title", "") or ""),
            str(item.get("section", "") or ""),
            str(item.get("knowledge_source", "") or ""),
        ]
    )

    if item_topic in matched_topics:
        score += 0.65

    if any(
        authority.lower() in item_authority.lower()
        or item_authority.lower() in authority.lower()
        for authority in matched_authorities
    ):
        score += 0.25

    q_tokens = {
        token for token in re.findall(r"[a-z0-9]+", _normalise(query))
        if len(token) >= 4
    }
    metadata_tokens = set(re.findall(r"[a-z0-9]+", _normalise(document_text)))
    if q_tokens and metadata_tokens:
        overlap = len(q_tokens & metadata_tokens) / len(q_tokens)
        score += min(overlap, 1.0) * 0.10

    return min(score, 1.0)


def _term_overlap_score(query: str, content: str) -> float:
    """Lightweight lexical overlap signal independent of TF-IDF."""
    q_tokens = {
        token for token in re.findall(r"[a-z0-9]+", _normalise(query))
        if len(token) >= 4
    }
    content_tokens = set(re.findall(r"[a-z0-9]+", _normalise(content)))

    if not q_tokens:
        return 0.0

    return len(q_tokens & content_tokens) / len(q_tokens)


def query_legal_database(query_text: str, top_k: int = 3) -> List[Dict]:
    """
    Query the offline legal knowledge base using hybrid retrieval.

    The public return structure remains backward-compatible with the
    existing RAG assistant while exposing additional retrieval metadata.
    """
    offline_db_path = os.path.join(DB_DIR, "offline_vectorstore.pkl")

    if not os.path.exists(offline_db_path):
        pf(
            "[ERROR] No Vector Database found. Please run: "
            "python scripts/vector_store.py first."
        )
        return []

    try:
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        pf("[ERROR] scikit-learn is required for retrieval.")
        return []

    with open(offline_db_path, "rb") as f:
        data = pickle.load(f)

    chunks = data.get("chunks", [])
    vectorizer = data.get("vectorizer")
    matrix = data.get("matrix")

    if not chunks or vectorizer is None or matrix is None:
        pf("[ERROR] Vector store is incomplete or empty.")
        return []

    query = str(query_text or "").strip()
    if not query:
        return []

    # Lexical retrieval from the existing vector store.
    query_vec = vectorizer.transform([query])
    lexical_scores = cosine_similarity(query_vec, matrix).flatten()

    matched_topics = _matched_topics(query)
    matched_authorities = _matched_authorities(query)

    candidates = []

    for idx, item in enumerate(chunks):
        lexical_score = float(lexical_scores[idx])
        metadata_score = _metadata_score(
            query,
            item,
            matched_topics,
            matched_authorities,
        )
        overlap_score = _term_overlap_score(
            query,
            item.get("content", ""),
        )
        exact_reference_score = _exact_reference_score(query, item)

        # Weighted hybrid score.
        #
        # TF-IDF remains the primary evidence signal.
        # Metadata routes legal queries to the right topic/source.
        # Exact legal references get an additional precision boost.
        # Term overlap remains a small stability signal.
        hybrid_score = (
            0.55 * lexical_score
            + 0.15 * metadata_score
            + 0.20 * exact_reference_score
            + 0.10 * overlap_score
        )

        # Avoid returning completely unrelated zero-score chunks.
        if hybrid_score <= 0.005:
            continue

        candidates.append(
            (
                hybrid_score,
                lexical_score,
                metadata_score,
                overlap_score,
                exact_reference_score,
                idx,
                item,
            )
        )

    if not candidates:
        return []

    candidates.sort(
        key=lambda row: (
            row[4],  # exact legal-reference score
            row[0],  # hybrid score
        ),
        reverse=True,
    )

    # Keep results diverse across documents where possible.
    selected = []
    seen_documents = set()

    for candidate in candidates:
        document_title = str(candidate[6].get("document_title", "") or "")

        if (
            document_title
            and document_title in seen_documents
            and len(selected) < top_k
        ):
            continue

        selected.append(candidate)
        if document_title:
            seen_documents.add(document_title)

        if len(selected) >= top_k:
            break

    # If document diversity left us short, fill from the remaining ranking.
    if len(selected) < top_k:
        selected_indices = {row[4] for row in selected}
        for candidate in candidates:
            if candidate[4] in selected_indices:
                continue
            selected.append(candidate)
            if len(selected) >= top_k:
                break

    retrieved = []

    for (
        hybrid_score,
        lexical_score,
        metadata_score,
        overlap_score,
        exact_reference_score,
        idx,
        item,
    ) in selected:
        retrieved.append(
            {
                "chunk_id": item.get("chunk_id", ""),
                "document_title": item.get("document_title", ""),
                "section": item.get("section", ""),
                "page": item.get("page", item.get("page_number")),
                "jurisdiction": item.get("jurisdiction", "India"),
                "authority": item.get("authority", ""),
                "topic": item.get("topic", ""),
                "knowledge_source": item.get("knowledge_source", ""),
                "content": item.get("content", ""),
                "relevance_score": round(float(hybrid_score), 4),
                "lexical_score": round(float(lexical_score), 4),
                "metadata_score": round(float(metadata_score), 4),
                "exact_reference_score": round(float(exact_reference_score), 4),
                "term_overlap_score": round(float(overlap_score), 4),
            }
        )

    return retrieved


if __name__ == "__main__":
    test_query = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Can I patent traditional Ayurvedic knowledge under Section 3(p)?"
    )

    pf(
        f"\n[SEARCH] Querying Database for: '{test_query}'\n"
        + "-" * 65
    )

    results = query_legal_database(test_query, top_k=3)

    if not results:
        pf("No matches found or database not initialized.")

    for i, res in enumerate(results, 1):
        pf(
            f"\n[{i}] Source: {res['document_title']} "
            f"| Section: {res['section']}"
        )
        pf(
            f"    Authority: {res['authority']} "
            f"| Topic: {res.get('topic', '')}"
        )
        pf(
            f"    Hybrid: {res['relevance_score']} "
            f"| TF-IDF: {res['lexical_score']} "
            f"| Metadata: {res['metadata_score']} "
            f"| Exact Ref: {res.get('exact_reference_score', 0.0)}"
        )
        pf(f"    Passage: {res['content'][:300]}...")
