"""Duplicate check using normalized token overlap as a portable pgvector substitute."""
from typing import Optional
import re
from ...config import get_settings

def check_duplicates(state):
    """Compare intake text with existing complaints and return explainable matches."""
    settings = get_settings()
    text = str(state.get("extracted_fields", {})).lower()
    tokens = set(re.findall(r"[a-z0-9]{4,}", text))
    matches = []
    for item in state.get("existing_records") or []:
        other = set(re.findall(r"[a-z0-9]{4,}", str(item).lower()))
        similarity = len(tokens & other) / max(1, len(tokens | other))
        if similarity >= settings.duplicate_similarity_threshold:
            matches.append({"complaint_id": item.complaint_id, "similarity": round(similarity, 2)})
    return {**state, "duplicate_complaints": matches, "processing_status": "duplicates_checked"}
