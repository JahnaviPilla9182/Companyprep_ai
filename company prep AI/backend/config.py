"""
backend/config.py
Loads configuration from environment variables or Streamlit secrets.
Determines AI provider and operating mode.
"""
import os
from pathlib import Path

# Load .env file if present (local development)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass


def _get_secret(key: str, default: str = "") -> str:
    """Try Streamlit secrets first, then env vars, then default."""
    try:
        import streamlit as st
        val = st.secrets.get(key, "")
        if val:
            return str(val)
    except Exception:
        pass
    return os.environ.get(key, default)


# AI Provider selection
AI_PROVIDER: str = _get_secret("AI_PROVIDER", "gemini").lower()

# API Keys
GEMINI_API_KEY: str = _get_secret("GEMINI_API_KEY", "")
GROQ_API_KEY: str = _get_secret("GROQ_API_KEY", "")

# Model names
GEMINI_MODEL: str = _get_secret("GEMINI_MODEL", "gemini-3.5-flash-lite")
GROQ_MODEL: str = _get_secret("GROQ_MODEL", "llama-3.1-8b-instant")

# Determine operating mode
_forced_mode = _get_secret("APP_MODE", "").lower()
if _forced_mode == "demo":
    DEMO_MODE: bool = True
elif _forced_mode == "production":
    DEMO_MODE: bool = False
else:
    # Auto-detect: demo if no key is available for the chosen provider
    if AI_PROVIDER == "groq":
        DEMO_MODE = not bool(GROQ_API_KEY)
    else:
        DEMO_MODE = not bool(GEMINI_API_KEY)

# LLM request timeout seconds
LLM_TIMEOUT: int = int(_get_secret("LLM_TIMEOUT", "60"))

APP_NAME = "CompanyPrep AI"
APP_VERSION = "1.0.0"
