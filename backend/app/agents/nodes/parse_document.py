"""Extraction node: use Groq when configured, otherwise a deterministic demo parser."""
from typing import Optional
import json, re
from ..state import ComplaintState
from ..prompts.extraction_prompt import EXTRACTION_SYSTEM_PROMPT

FIELDS = ["complaint_source", "customer_name", "product_name", "product_strength", "batch_lot_number", "manufacturing_date", "expiry_date", "quantity_affected", "quantity_unit", "complaint_type", "complaint_date", "description"]
FIELD_LABELS = {
    "batch_lot_number": ("batch lot number", "batch number", "lot number"),
    "quantity_affected": ("quantity affected", "affected quantity", "quantity"),
}

MONTHS = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}

def _canonical_date(value):
    """Return an ISO date, using day one when only month/year is supplied."""
    if not value:
        return None
    text = str(value).strip()
    iso = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if iso:
        return f"{iso.group(1)}-{int(iso.group(2)):02d}-{int(iso.group(3)):02d}"
    month_year = re.fullmatch(r"([A-Za-z]+)\s+(\d{4})", text)
    if month_year and month_year.group(1).lower() in MONTHS:
        return f"{month_year.group(2)}-{MONTHS[month_year.group(1).lower()]}-01"
    numeric_month_year = re.fullmatch(r"(\d{1,2})[/-](\d{4})", text)
    if numeric_month_year:
        return f"{numeric_month_year.group(2)}-{int(numeric_month_year.group(1)):02d}-01"
    return None

def _date_from_text(text: str, label: str):
    """Read a date after a field label when the model omits or nulls it."""
    match = re.search(
        rf"{re.escape(label)}\s*(?:is|:|-)?\s*"
        rf"((?:{'|'.join(MONTHS.keys())})\s+\d{{4}}|\d{{1,2}}[/-]\d{{4}}|\d{{4}}-\d{{1,2}}-\d{{1,2}})",
        text,
        re.IGNORECASE,
    )
    return _canonical_date(match.group(1)) if match else None

def _normalize_fields(fields: dict, text: str) -> dict:
    """Apply deterministic domain normalization after the LLM or fallback parser."""
    normalized = {**fields}

    # In conversational reports, the organization before 'reported' is the customer.
    reporter = re.search(r"(?:^|[.!?])\s*([A-Z][A-Za-z0-9&.' -]{1,100}?)\s+reported\b", text)
    if not reporter:
        reporter = re.search(r"\b([A-Z][A-Za-z0-9&.' -]{1,100}?)\s+reported\b", text)
    if reporter:
        customer = reporter.group(1).strip(" .,-")
        normalized["customer_name"] = customer
        lower_customer = customer.lower()
        channel_map = (
            ("pharmacy", "Pharmacy"),
            ("hospital", "Hospital"),
            ("clinic", "Clinic"),
            ("patient", "Patient"),
            ("doctor", "Healthcare Professional"),
        )
        for keyword, channel in channel_map:
            if keyword in lower_customer:
                normalized["complaint_source"] = channel
                break

    for field in ("manufacturing_date", "expiry_date", "complaint_date"):
        normalized[field] = _canonical_date(normalized.get(field)) or _date_from_text(text, field.replace("_", " "))

    # The complaint is being entered now, so use today's date when the source
    # report does not provide a separate incident date.
    if not normalized.get("complaint_date"):
        from datetime import date
        normalized["complaint_date"] = date.today().isoformat()

    return normalized

def _demo_extract(text: str) -> dict:
    """Extract common labeled fields so the project works without an API key."""
    def value(label: str):
        match = re.search(rf"{re.escape(label)}\s*(?:[:=-]\s*|\s+)([^\n.]+)", text, re.I)
        return match.group(1).strip().splitlines()[0] if match else None
    fields = {
        field: next((value(label) for label in FIELD_LABELS.get(field, (field.replace("_", " "),)) if value(label)), None)
        for field in FIELDS
    }
    fields["description"] = value("description") or text[:1200]
    fields["quantity_affected"] = float(fields["quantity_affected"]) if fields["quantity_affected"] and re.fullmatch(r"\d+(\.\d+)?", fields["quantity_affected"]) else None
    fields["quantity_unit"] = fields["quantity_unit"] or "kg"
    return _normalize_fields(fields, text)

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
            fields = _normalize_fields({**fields, **parsed}, state["raw_text"])
        except Exception as exc:
            state.setdefault("errors", []).append(f"AI extraction failed: {exc}")
            if not settings.enable_fallback_mocks:
                raise
    elif not settings.enable_fallback_mocks:
        raise RuntimeError("Document parsing requires Groq API key when fallbacks are disabled.")
        
    return {**state, "extracted_fields": fields, "processing_status": "extracted"}
