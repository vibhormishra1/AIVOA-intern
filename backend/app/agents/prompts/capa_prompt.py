"""LLM prompt for CAPA recommendations."""
from typing import Optional
CAPA_SYSTEM_PROMPT = """Suggest 2-4 practical CAPA actions for this complaint. Return a JSON array; each item has action_type (Corrective or Preventive), description, regulatory_ref. Recommendations assist QA review and are not final approval."""
