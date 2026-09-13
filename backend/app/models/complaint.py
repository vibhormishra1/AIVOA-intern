from __future__ import annotations
from typing import Optional
"""Complaint persistence model."""
from datetime import date, datetime
from sqlalchemy import Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
from ..database import Base

class Complaint(Base):
    """Main QMS complaint record, including AI audit metadata."""
    __tablename__ = "complaints"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    complaint_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    complaint_source: Mapped[Optional[str]] = mapped_column(String(100))
    customer_name: Mapped[Optional[str]] = mapped_column(String(200))
    product_name: Mapped[Optional[str]] = mapped_column(String(200))
    product_strength: Mapped[Optional[str]] = mapped_column(String(100))
    batch_lot_number: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    manufacturing_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    quantity_affected: Mapped[Optional[float]] = mapped_column(Float)
    quantity_unit: Mapped[str] = mapped_column(String(20), default="kg")
    complaint_type: Mapped[Optional[str]] = mapped_column(String(100))
    complaint_date: Mapped[Optional[date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    initial_severity: Mapped[Optional[str]] = mapped_column(String(50))
    priority: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="Pending Triage", index=True)
    ai_extracted: Mapped[bool] = mapped_column(default=False)
    raw_document_text: Mapped[Optional[str]] = mapped_column(Text)
    ai_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
