"""Complaint CRUD and response serialization."""
from typing import Optional
from datetime import datetime
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from ..models import Complaint

def next_complaint_id(db: Session) -> str:
    """Generate the human-friendly CMP-YYYY-NNNN identifier."""
    year = datetime.now().year
    count = db.scalar(select(Complaint).where(Complaint.complaint_id.like(f"CMP-{year}-%")).count()) if False else len(db.scalars(select(Complaint).where(Complaint.complaint_id.like(f"CMP-{year}-%"))).all())
    return f"CMP-{year}-{count + 1:04d}"

def create_complaint(db: Session, payload: dict) -> Complaint:
    """Persist validated form data and return the saved ORM record."""
    complaint = Complaint(complaint_id=next_complaint_id(db), **payload)
    db.add(complaint); db.commit(); db.refresh(complaint)
    return complaint

def list_complaints(db: Session, status=None, severity=None, search=None):
    """Return dashboard records filtered by status, severity, or text search."""
    query = select(Complaint).order_by(Complaint.created_at.desc())
    if status: query = query.where(Complaint.status == status)
    if severity: query = query.where(Complaint.initial_severity == severity)
    if search: query = query.where(or_(Complaint.complaint_id.ilike(f"%{search}%"), Complaint.customer_name.ilike(f"%{search}%")))
    return list(db.scalars(query))
