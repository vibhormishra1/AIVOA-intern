"""Centralized environment-backed application settings."""
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""
    database_url: str = "sqlite:///./aivoa.db"
    groq_api_key: str = ""
    allowed_origins: str = "http://localhost:3000"
    app_env: str = "development"
    model_extraction: str = "gemma2-9b-it"
    model_reasoning: str = "llama-3.3-70b-versatile"
    
    # App logic parameters
    duplicate_similarity_threshold: float = 0.25
    risk_score_critical: int = 85
    risk_score_major: int = 65
    risk_score_minor: int = 30
    enable_fallback_mocks: bool = True
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self) -> list[str]:
        """Return comma-separated CORS origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

@lru_cache
def get_settings() -> Settings:
    """Create the cached settings object used by API services."""
    return Settings()
