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

@router.post("/extract")
async def extract(request: ComplaintExtractionRequest, db: Session = Depends(get_db)):
    """Extract fields and AI metadata from pasted text or an uploaded document."""
    return await ai_service.extract_complaint(request.file_content, request.file_type, db)

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

@router.get("/{complaint_id}")
async def get_one(complaint_id: int, db: Session = Depends(get_db)):
    """Return one full complaint record."""
    item = db.get(Complaint, complaint_id)
    if not item: raise HTTPException(404, "Complaint not found")
    return {column.name: getattr(item, column.name) for column in Complaint.__table__.columns}

@router.post("/{complaint_id}/chat")
async def chat(complaint_id: int, request: ChatRequest, db: Session = Depends(get_db)):
    """Persist a user question, generate a contextual answer, and persist it."""
    complaint = db.get(Complaint, complaint_id)
    if not complaint: raise HTTPException(404, "Complaint not found")
    db.add(ChatMessage(complaint_id=complaint.id, role="user", content=request.message))
    answer = await ai_service.chat_with_complaint(complaint, request.message)
    db.add(ChatMessage(complaint_id=complaint.id, role="assistant", content=answer)); db.commit()
    return {"role": "assistant", "response": answer}
