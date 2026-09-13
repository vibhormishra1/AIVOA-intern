"""Application service for AI workflow and copilot responses."""
from typing import Optional
from ..agents.graph import run_complaint_graph
from ..config import get_settings

async def extract_complaint(raw_text, file_type, db):
    """Run the graph and return the UI-shaped extraction response."""
    existing = db.query(type("ComplaintProxy", (), {})) if False else []
    result = await run_complaint_graph(raw_text, file_type, existing)
    return {"data": result}

import json
import io

def parse_pdf_bytes(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except ImportError:
        return "PyMuPDF not installed, unable to read PDF."
    except Exception as e:
        return f"Error reading PDF: {e}"

async def chat_with_complaint(complaint, message):
    """Answer a copilot question using complaint context and return structured JSON."""
    settings = get_settings()
    
    fallback_response = {"response": f"For {complaint.product_name or 'this complaint'} ({complaint.complaint_id}), review the batch record, retained samples, and complaint trend before making a final QA decision. (AI Copilot requires Groq API Key)", "updated_fields": {}}
    
    if not settings.groq_api_key:
        return fallback_response
        
    system_prompt = f"""You are an AI Copilot assisting a pharmaceutical QA agent.
You are helping them with complaint {complaint.complaint_id} for product {complaint.product_name}.
Current status: {complaint.status}. 
Priority: {complaint.priority}. 
Severity: {complaint.initial_severity}.
Complaint description: {complaint.description}

You must respond in strictly valid JSON format.
Your JSON must contain two keys:
1. "response": A string containing your conversational reply to the user. Provide helpful, context-aware answers. Never make final QA decisions.
2. "updated_fields": A dictionary of any complaint form fields the user wants to update based on their message. The keys must match the database schema (e.g., 'batch_lot_number', 'quantity_affected', 'product_name'). If no fields need updating, return an empty dictionary {{}}.
"""

    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=settings.groq_api_key)
        response = await client.chat.completions.create(
            model=settings.model_reasoning,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as exc:
        return {"response": f"AI Copilot encountered an error: {exc}. Please review the batch records manually.", "updated_fields": {}}
