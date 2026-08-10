"""ProjectForge AI — Application Configuration."""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- LLM Providers ---
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""

    # --- Web Search ---
    TAVILY_API_KEY: str = ""

    # --- Database ---
    DATABASE_URL: str = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/projectforge"

    # --- Application ---
    SECRET_KEY: str = "change-me-to-a-random-secret"
    DEBUG: bool = True
    BACKEND_URL: str = "http://localhost:8000"
    VITE_BACKEND_URL: str = "http://localhost:8000"

    # --- Per-Agent Model Configuration ---
    # Format: "provider/model-name" e.g. "gemini/gemini-2.0-flash"
    REQUIREMENT_AGENT_MODEL: str = ""
    TECHNOLOGY_AGENT_MODEL: str = ""
    ARCHITECTURE_AGENT_MODEL: str = ""
    TASK_PLANNER_AGENT_MODEL: str = ""
    TIMELINE_AGENT_MODEL: str = ""
    CRITIC_AGENT_MODEL: str = ""

    # --- JWT ---
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    # ---- Helpers ----
    def get_agent_model(self, agent_name: str) -> str:
        """Return the configured model string for a given agent, or a valid fallback.

        Guarantees that the returned string is in 'provider/model-name' format
        for an active API key and NEVER returns an API key.
        """
        mapping = {
            "requirement_analyst": self.REQUIREMENT_AGENT_MODEL,
            "technology_advisor": self.TECHNOLOGY_AGENT_MODEL,
            "architecture": self.ARCHITECTURE_AGENT_MODEL,
            "task_planner": self.TASK_PLANNER_AGENT_MODEL,
            "timeline": self.TIMELINE_AGENT_MODEL,
            "critic": self.CRITIC_AGENT_MODEL,
        }
        model = (mapping.get(agent_name, "") or "").strip()

        # Check format and guard against accidental API key strings
        has_valid_format = bool(model and "/" in model)
        is_api_key = False
        if model:
            if (self.GEMINI_API_KEY and model == self.GEMINI_API_KEY) or \
               (self.GROQ_API_KEY and model == self.GROQ_API_KEY) or \
               (self.OPENROUTER_API_KEY and model == self.OPENROUTER_API_KEY) or \
               model.startswith("AIza") or model.startswith("gsk_") or \
               model.startswith("sk-or-") or model.startswith("AQ."):
                is_api_key = True

        # Check if the provider requested in model string has a configured API key
        provider_has_key = True
        if has_valid_format and not is_api_key:
            provider = model.split("/", 1)[0].lower()
            if provider == "gemini" and not self.GEMINI_API_KEY:
                provider_has_key = False
            elif provider == "groq" and not self.GROQ_API_KEY:
                provider_has_key = False
            elif provider == "openrouter" and not self.OPENROUTER_API_KEY:
                provider_has_key = False

        if has_valid_format and not is_api_key and provider_has_key:
            return model

        # Fallback to active providers (preferring Groq/OpenRouter if available to avoid Gemini 429 quota)
        if self.GROQ_API_KEY:
            return "groq/llama-3.3-70b-versatile"
        elif self.OPENROUTER_API_KEY:
            return "openrouter/google/gemini-2.0-flash-exp:free"
        elif self.GEMINI_API_KEY:
            return "gemini/gemini-2.0-flash"

        return ""

    def has_any_llm_key(self) -> bool:
        """Check if at least one LLM provider API key is configured."""
        return bool(self.GEMINI_API_KEY or self.GROQ_API_KEY or self.OPENROUTER_API_KEY)


settings = Settings()
