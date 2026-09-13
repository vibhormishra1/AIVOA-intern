"""Extraction node: use Groq when configured, otherwise a deterministic demo parser."""
from typing import Optional
import json, re
from ..state import ComplaintState
from ..prompts.extraction_prompt import EXTRACTION_SYSTEM_PROMPT

FIELDS = ["complaint_source", "customer_name", "product_name", "product_strength", "batch_lot_number", "manufacturing_date", "expiry_date", "quantity_affected", "quantity_unit", "complaint_type", "complaint_date", "description"]

def _demo_extract(text: str) -> dict:
    """Extract common labeled fields so the project works without an API key."""
    def value(label: str):
        match = re.search(rf"{re.escape(label)}\s*[:=-]\s*(.+)", text, re.I)
        return match.group(1).strip().splitlines()[0] if match else None
    fields = {field: value(field.replace("_", " ")) for field in FIELDS}
    fields["description"] = value("description") or text[:1200]
    fields["quantity_affected"] = float(fields["quantity_affected"]) if fields["quantity_affected"] and re.fullmatch(r"\d+(\.\d+)?", fields["quantity_affected"]) else None
    fields["quantity_unit"] = fields["quantity_unit"] or "kg"
    return fields

async def parse_document(state: ComplaintState) -> ComplaintState:
    """Parse raw input with Groq JSON mode or the local demo parser."""
    from ...config import get_settings
    settings = get_settings()
    
    fields = _demo_extract(state["raw_text"]) if settings.enable_fallback_mocks else {}
    
    if settings.groq_api_key:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=settings.groq_api_key)
            response = await client.chat.completions.create(model=settings.model_extraction, temperature=0.1, response_format={"type": "json_object"}, messages=[{"role": "system", "content": EXTRACTION_SYSTEM_PROMPT}, {"role": "user", "content": state["raw_text"]}])
            parsed = json.loads(response.choices[0].message.content)
            fields = {**fields, **parsed}
        except Exception as exc:
            state.setdefault("errors", []).append(f"AI extraction failed: {exc}")
            if not settings.enable_fallback_mocks:
                raise
    elif not settings.enable_fallback_mocks:
        raise RuntimeError("Document parsing requires Groq API key when fallbacks are disabled.")
        
    return {**state, "extracted_fields": fields, "processing_status": "extracted"}
