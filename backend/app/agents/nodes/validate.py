"""Pure-Python regulatory completeness check."""
from typing import Optional
REQUIRED_FIELDS = ["customer_name", "product_name", "batch_lot_number", "complaint_date", "description"]

def validate_completeness(state):
    """Flag missing high-value intake fields and compute a transparent score."""
    fields = state.get("extracted_fields", {})
    missing = [field for field in REQUIRED_FIELDS if not fields.get(field)]
    score = round((len(REQUIRED_FIELDS) - len(missing)) / len(REQUIRED_FIELDS) * 100)
    return {**state, "missing_fields": missing, "completeness_score": score, "processing_status": "validated"}
