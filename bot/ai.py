"""freelm AI wrapper with health checks and provider status."""
import os
import logging
from typing import Optional
from freelm import FreeLLM
from dotenv import load_dotenv

# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

logger = logging.getLogger(__name__)

_client: Optional[FreeLLM] = None


def get_client() -> FreeLLM:
    """Get or create FreeLLM client singleton."""
    global _client
    if _client is None:
        keyless = os.getenv("FREELM_KEYLESS", "auto")
        _client = FreeLLM.from_env(keyless=keyless)
        logger.info("FreeLLM client initialized")
        log_provider_health()
    return _client


def log_provider_health() -> None:
    """Log which providers have working keys."""
    client = get_client()
    try:
        health = client.health()
        for p in health:
            status = "OK" if p["ready"] and not p["disabled"] else "FAIL"
            logger.info(f"Provider: {p['provider']} | Key: {p['key']} | Tier: {p['tier']} | {status}")
    except Exception as e:
        logger.warning(f"Health check failed: {e}")


def ask_ai(prompt: str, system: str = None, model: str = "auto") -> str:
    """
    Send prompt to freelm, return text response.
    Falls back automatically across providers.
    """
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat(messages, model=model)
        return response.text
    except Exception as e:
        logger.error(f"All providers failed: {e}")
        return "Sorry, I'm having trouble thinking right now. All AI providers are unavailable."


def ask_ai_with_provider(prompt: str, system: str = None, model: str = "auto") -> tuple[str, str]:
    """
    Returns (response_text, provider_name) for logging which provider answered.
    """
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat(messages, model=model)
        provider = getattr(response, 'provider', 'unknown')
        return response.text, str(provider)
    except Exception as e:
        logger.error(f"All providers failed: {e}")
        return "Sorry, I'm having trouble thinking right now.", "none"


def close_client() -> None:
    """Cleanup on shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None