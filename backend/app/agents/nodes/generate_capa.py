"""CAPA suggestion node utilizing Groq for AI-powered recommendations."""
from typing import Optional
import json
from ...config import get_settings

SYSTEM_PROMPT = """
You are an expert pharmaceutical Quality Assurance agent.
Your task is to generate Corrective and Preventive Action (CAPA) suggestions based on the provided complaint details and risk classification.
Assess the complaint details and respond ONLY with a valid JSON object matching this schema:
{
  "capa_suggestions": [
    {
      "action_type": "<Corrective | Preventive>",
      "description": "<detailed description of the recommended action>",
      "regulatory_ref": "<e.g., FDA 21 CFR 211.198, ICH Q10>"
    }
  ]
}

Provide 1-2 Corrective actions and 1-2 Preventive actions.
"""

def _fallback_capa(severity: str) -> list:
    """Deterministic fallback if API fails."""
    if severity not in {"Critical", "Major"}:
        return []
    return [
        {"action_type": "Corrective", "description": "Quarantine the affected batch and review batch records, test results, and retained samples.", "regulatory_ref": "FDA 21 CFR 211.198"},
        {"action_type": "Preventive", "description": "Trend similar complaints and update the relevant SOP or in-process control after root-cause confirmation.", "regulatory_ref": "ICH Q10"}
    ]

async def generate_capa(state):
    """Generate review-ready CAPA suggestions for Critical or Major complaints."""
    severity = state.get("risk_classification", {}).get("initial_severity")
    if severity not in {"Critical", "Major"}:
        return {**state, "capa_suggestions": [], "processing_status": "capa_generated"}
        
    text = f"Severity: {severity}\nExtracted Fields: {state.get('extracted_fields', {})}\nRaw Text: {state.get('raw_text', '')}"
    
    settings = get_settings()
    suggestions = None
    
    if settings.groq_api_key:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=settings.groq_api_key)
            response = await client.chat.completions.create(
                model=settings.model_reasoning,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ]
            )
            result = json.loads(response.choices[0].message.content)
            suggestions = result.get("capa_suggestions")
        except Exception as exc:
            state.setdefault("errors", []).append(f"AI CAPA generation failed, using fallback: {exc}")
            
    if not suggestions:
        suggestions = _fallback_capa(severity)
        
    return {**state, "capa_suggestions": suggestions, "processing_status": "capa_generated"}
