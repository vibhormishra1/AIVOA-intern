from __future__ import annotations
from typing import Optional
"""Pydantic contracts for complaint APIs."""
from datetime import date
from pydantic import BaseModel, Field

class ComplaintExtractionRequest(BaseModel):
    """Raw document payload submitted for AI extraction."""
    file_content: str = Field(min_length=1, max_length=2_000_000)
    file_type: str = "txt"
    file_name: str = "pasted_text.txt"

class ComplaintCreateRequest(BaseModel):
    """Validated form payload written to the complaint table."""
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_lot_number: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    quantity_affected: Optional[float] = None
    quantity_unit: str = "kg"
    complaint_type: Optional[str] = None
    complaint_date: Optional[date] = None
    description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None
    raw_document_text: Optional[str] = None
    ai_metadata: dict = {}

class ChatRequest(BaseModel):
    """Question sent to the complaint copilot."""
    message: str = Field(min_length=1, max_length=4000)
