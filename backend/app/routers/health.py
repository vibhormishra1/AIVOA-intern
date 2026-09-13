from __future__ import annotations
from typing import Optional
"""Health endpoint for container and local smoke checks."""
from fastapi import APIRouter
router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    """Return a lightweight service liveness response."""
    return {"status": "ok", "service": "aivoa-complaints"}
