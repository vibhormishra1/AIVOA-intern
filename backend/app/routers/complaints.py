from __future__ import annotations
from typing import Optional
"""HTTP routes kept thin over services and graph orchestration."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.complaint import ComplaintCreateRequest, ComplaintExtractionRequest, ChatRequest
from ..services import complaint_service, ai_service
from ..models import Complaint, ChatMessage

router = APIRouter(prefix="/api/v1/complaints", tags=["complaints"])

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

@router.post("/extract")
async def extract(
    db: Session = Depends(get_db),
    file: Optional[UploadFile] = File(None),
    file_content: Optional[str] = Form(None),
    file_type: str = Form("txt")
):
    """Extract fields and AI metadata from pasted text or an uploaded document."""
    text_content = ""
    if file:
        file_bytes = await file.read()
        if file.filename.lower().endswith(".pdf"):
            text_content = ai_service.parse_pdf_bytes(file_bytes)
            file_type = "pdf"
        else:
            text_content = file_bytes.decode('utf-8', errors='ignore')
    elif file_content:
        text_content = file_content
        
    if not text_content:
        raise HTTPException(400, "No text or file provided")
        
    return await ai_service.extract_complaint(text_content, file_type, db)

@router.post("")
async def create(request: ComplaintCreateRequest, db: Session = Depends(get_db)):
    """Validate, persist, and identify the new complaint."""
    complaint = complaint_service.create_complaint(db, request.model_dump())
    return {"complaint_id": complaint.complaint_id, "id": complaint.id, "status": complaint.status}

@router.get("")
async def list_all(status: Optional[str] = None, severity: Optional[str] = None, search: Optional[str] = None, db: Session = Depends(get_db)):
    """Return dashboard rows with optional filters."""
    records = complaint_service.list_complaints(db, status, severity, search)
    return [{"id": x.id, "complaint_id": x.complaint_id, "customer_name": x.customer_name, "product_name": x.product_name, "initial_severity": x.initial_severity, "priority": x.priority, "status": x.status, "created_at": x.created_at} for x in records]

def _find_complaint(db: Session, complaint_id: str):
    """Resolve either the internal numeric ID or public CMP-YYYY-NNNN ID."""
    if complaint_id.isdigit():
        item = db.get(Complaint, int(complaint_id))
    else:
        item = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    return item

@router.get("/{complaint_id}")
async def get_one(complaint_id: str, db: Session = Depends(get_db)):
    """Return one full complaint record."""
    item = _find_complaint(db, complaint_id)
    if not item: raise HTTPException(404, "Complaint not found")
    return {column.name: getattr(item, column.name) for column in Complaint.__table__.columns}

@router.post("/{complaint_id}/chat")
async def chat(complaint_id: str, request: ChatRequest, db: Session = Depends(get_db)):
    """Persist a user question, generate a contextual answer, and return form updates."""
    complaint = _find_complaint(db, complaint_id)
    if not complaint: raise HTTPException(404, "Complaint not found")
    db.add(ChatMessage(complaint_id=complaint.id, role="user", content=request.message))
    
    # Get structured JSON back from AI
    result = await ai_service.chat_with_complaint(complaint, request.message)
    response_text = result.get("response", "No response generated.")
    updated_fields = result.get("updated_fields", {})
    
    db.add(ChatMessage(complaint_id=complaint.id, role="assistant", content=response_text))
    db.commit()
    return {"role": "assistant", "response": response_text, "updated_fields": updated_fields}
