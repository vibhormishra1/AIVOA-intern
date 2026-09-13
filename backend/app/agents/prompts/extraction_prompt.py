"""LLM prompt for conservative structured complaint extraction."""
from typing import Optional
EXTRACTION_SYSTEM_PROMPT = """Extract a pharmaceutical customer complaint into JSON. Use these exact keys: complaint_source, customer_name, product_name, product_strength, batch_lot_number, manufacturing_date, expiry_date, quantity_affected, quantity_unit, complaint_type, complaint_date, description.

Separate the reporting channel from the organization. For example, in 'Apollo Pharmacy reported a defect', complaint_source is 'Pharmacy' and customer_name is 'Apollo Pharmacy'. complaint_source should be a channel such as Pharmacy, Hospital, Clinic, Patient, Healthcare Professional, Email, Phone, or Other; customer_name is the named organization or person.

Dates must be YYYY-MM-DD. If the text provides only a month and year, use the first day of that month as the canonical date (for example, March 2026 becomes 2026-03-01). Do not invent a month or year. complaint_type must be one of Quality Defect, Packaging Issue, Labeling Error, Contamination, Adverse Event, Delivery Issue, Documentation Error, Other. Use null when a value is absent."""
