"""FastAPI application entry point."""
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import Base, engine
from . import models
from .routers import complaints, health

Base.metadata.create_all(bind=engine)
app = FastAPI(title="AIVOA Complaint Management API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=get_settings().origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router); app.include_router(complaints.router)
