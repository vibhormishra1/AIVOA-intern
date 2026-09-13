from __future__ import annotations
from typing import Optional
"""CAPA recommendation persistence model."""
from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class CapaAction(Base):
    """Corrective or preventive action linked to a complaint."""
    __tablename__ = "capa_actions"
    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"))
    action_type: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(200))
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), default="Open")
    regulatory_ref: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
