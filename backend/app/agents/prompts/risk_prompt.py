"""LLM prompt for safety-oriented triage."""
from typing import Optional
RISK_SYSTEM_PROMPT = """Classify a pharma complaint conservatively. Return JSON with risk_score (1-100), risk_category (High Risk, Medium Risk, Low Risk), initial_severity (Critical, Major, Minor, Informational), priority (Urgent, High, Medium, Low), and rationale. Patient safety and contamination signals increase risk."""
