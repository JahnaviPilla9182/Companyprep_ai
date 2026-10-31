"""
backend/services/llm_service.py
Abstracts Gemini and Groq API calls with demo fallback.
Never raises unhandled exceptions — always returns a string.
"""
import json
import sys
import time
from typing import Optional

try:
    from backend.config import (
        AI_PROVIDER, DEMO_MODE, GEMINI_API_KEY, GROQ_API_KEY,
        GEMINI_MODEL, GROQ_MODEL, LLM_TIMEOUT,
    )
except ImportError:
    from config import (
        AI_PROVIDER, DEMO_MODE, GEMINI_API_KEY, GROQ_API_KEY,
        GEMINI_MODEL, GROQ_MODEL, LLM_TIMEOUT,
    )

DEMO_NOTICE = "[DEMO MODE — AI provider not configured. Showing rule-based sample output.]"


def _call_gemini(prompt: str) -> str:
    """Call Gemini API and return text response."""
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            max_output_tokens=4096,
        ),
        request_options={"timeout": LLM_TIMEOUT},
    )
    return response.text


def _call_groq(prompt: str) -> str:
    """Call Groq API and return text response."""
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=4096,
        timeout=LLM_TIMEOUT,
    )
    return response.choices[0].message.content


def generate(prompt: str, structured: bool = False, retries: int = 2) -> str:
    """
    Generate AI content from prompt.
    Returns a string (JSON text if structured=True and the model cooperates).
    In demo mode returns a placeholder string.
    """
    if DEMO_MODE:
        return DEMO_NOTICE

    last_error = ""
    for attempt in range(retries + 1):
        try:
            if AI_PROVIDER == "groq":
                return _call_groq(prompt)
            else:
                return _call_gemini(prompt)
        except Exception as e:
            err_str = str(e)
            last_error = err_str
            print(f"[LLM] Attempt {attempt + 1} failed: {err_str}", file=sys.stderr)
            if "429" in err_str or "quota" in err_str.lower():
                time.sleep(min(2 ** attempt, 30))
            elif attempt < retries:
                time.sleep(1)
            else:
                break

    return f"[AI generation failed: {last_error[:200]}. Showing demo content instead.] {DEMO_NOTICE}"


def generate_json(prompt: str, fallback: dict = None, retries: int = 2) -> dict:
    """
    Generate structured JSON from the AI.
    Wraps the prompt with JSON instructions and parses the result.
    Returns fallback dict on failure.
    """
    json_prompt = (
        prompt
        + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no code fences, no extra text."
    )
    raw = generate(json_prompt, structured=True, retries=retries)
    if raw.startswith("[DEMO") or raw.startswith("[AI generation"):
        return fallback or {}
    try:
        # Strip possible markdown code fences
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[LLM] JSON parse error: {e}", file=sys.stderr)
        return fallback or {}


def get_provider_info() -> dict:
    """Return current provider configuration info."""
    return {
        "provider": AI_PROVIDER if not DEMO_MODE else "demo",
        "model": (GEMINI_MODEL if AI_PROVIDER == "gemini" else GROQ_MODEL) if not DEMO_MODE else "N/A",
        "demo_mode": DEMO_MODE,
    }
