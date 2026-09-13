"""Application service for AI workflow and copilot responses."""
from typing import Optional
from ..agents.graph import run_complaint_graph
from ..config import get_settings

async def extract_complaint(raw_text, file_type, db):
    """Run the graph and return the UI-shaped extraction response."""
    existing = db.query(type("ComplaintProxy", (), {})) if False else []
    result = await run_complaint_graph(raw_text, file_type, existing)
    return {"data": result}

async def chat_with_complaint(complaint, message):
    """Answer a copilot question using complaint context without pretending to be QA approval."""
    settings = get_settings()
    
    if not settings.groq_api_key:
        return f"For {complaint.product_name or 'this complaint'} ({complaint.complaint_id}), review the batch record, retained samples, and complaint trend before making a final QA decision. (AI Copilot requires Groq API Key)"
        
    system_prompt = f"""You are an AI Copilot assisting a pharmaceutical QA agent.
You are helping them with complaint {complaint.complaint_id} for product {complaint.product_name}.
Current status: {complaint.status}. 
Priority: {complaint.priority}. 
Severity: {complaint.initial_severity}.
Complaint description: {complaint.description}

Provide helpful, context-aware answers. Never make final QA decisions; advise the user to review batch records and SOPs."""

    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=settings.groq_api_key)
        response = await client.chat.completions.create(
            model=settings.model_reasoning,
            temperature=0.3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as exc:
        return f"AI Copilot encountered an error: {exc}. Please review the batch records manually."
