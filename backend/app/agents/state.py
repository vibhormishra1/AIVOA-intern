"""Typed state shared by LangGraph nodes."""
from typing import Optional
from typing import Any, TypedDict

class ComplaintState(TypedDict, total=False):
    """State contract that makes each AI workflow step explicit and testable."""
    raw_text: str
    file_type: str
    extracted_fields: dict[str, Any]
    missing_fields: list[str]
    completeness_score: int
    risk_classification: dict[str, Any]
    duplicate_complaints: list[dict[str, Any]]
    capa_suggestions: list[dict[str, Any]]
    processing_status: str
    errors: list[str]
    existing_records: list

