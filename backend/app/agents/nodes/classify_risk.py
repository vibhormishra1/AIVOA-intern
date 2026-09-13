"""Risk triage node utilizing Groq for AI-powered assessment."""
from typing import Optional
import json
from ...config import get_settings

SYSTEM_PROMPT = """
You are an expert pharmaceutical Quality Assurance agent.
Your task is to classify the risk of a customer complaint based on patient safety and regulatory signals.
Assess the complaint details and respond ONLY with a valid JSON object matching this schema:
{
  "risk_score": <int between 0 and 100>,
  "risk_category": "<Low Risk | Medium Risk | High Risk>",
  "initial_severity": "<Minor | Major | Critical>",
  "priority": "<Low | Medium | High | Urgent>",
  "rationale": "<brief explanation of the classification based on QA principles>"
}

Guidelines:
- High Risk / Critical / Urgent (Score 80-100): Mentions of death, hospitalization, severe allergic reactions, wrong strength, adverse events.
- Medium Risk / Major / High (Score 50-79): Mentions of dissolution failure, broken product, foreign matter, leakage, recall.
- Low Risk / Minor / Medium or Low (Score 0-49): Packaging issues without product impact, missing labels, general inquiries.
"""

def _fallback_classify(text: str) -> dict:
    """Deterministic fallback if API fails."""
    high = any(word in text for word in ["death", "hospital", "contamination", "allergic", "wrong strength", "adverse event"])
    major = any(word in text for word in ["dissolution", "failed", "broken", "leak", "foreign matter", "recall"])
    score = 85 if high else 65 if major else 30
    return {
        "risk_score": score,
        "risk_category": "High Risk" if high else "Medium Risk" if major else "Low Risk",
        "initial_severity": "Critical" if high else "Major" if major else "Minor",
        "priority": "Urgent" if high else "High" if major else "Medium",
        "rationale": "Rule-based triage is a transparent fallback; QA must verify it."
    }

async def classify_risk(state):
    """Score patient-safety and regulatory signals into a reviewable triage result."""
    text = f"{state.get('extracted_fields', {})} {state.get('raw_text', '')}".lower()
    
    settings = get_settings()
    result = None
    
    if settings.groq_api_key:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=settings.groq_api_key)
            response = await client.chat.completions.create(
                model=settings.model_reasoning,
                temperature=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ]
            )
            result = json.loads(response.choices[0].message.content)
        except Exception as exc:
            state.setdefault("errors", []).append(f"AI risk classification failed, using fallback: {exc}")
    
    if not result:
        result = _fallback_classify(text)
        
    return {**state, "risk_classification": result, "processing_status": "risk_classified"}
