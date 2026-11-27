"""Classify user messages into intents (chat, generate, control)."""
import json
import logging
from typing import Dict, Any, Optional

from .ai import ask_ai

logger = logging.getLogger(__name__)

INTENT_SYSTEM_PROMPT = """
You are an intent classifier for a "What If" animation bot.
Classify the user's message into one of these intents:
- "chat": Regular conversation, questions, or comments.
- "generate": The user wants to create a new "What If" video.
- "control": The user wants to stop, cancel, or check the status of a video.

If the intent is "generate", extract:
- "topic": The core "What if..." question.
- "slug": A URL-friendly short version of the topic (e.g., "gravity-reversed").
- "title": A catchy title for the video.

Output valid JSON only.
Example: {"intent": "generate", "topic": "What if gravity reversed?", "slug": "gravity-reversed", "title": "What If: Gravity Reversed"}
Example: {"intent": "chat"}
Example: {"intent": "control", "action": "cancel"}
"""

def classify_intent(message: str) -> Dict[str, Any]:
    """Classify user intent using AI."""
    # Simple keyword shortcuts for speed/cost
    msg = message.lower().strip()
    if msg in ["stop", "cancel", "abort"]:
        return {"intent": "control", "action": "cancel"}
    if msg in ["status", "progress"]:
        return {"intent": "control", "action": "status"}
    if msg.startswith("/what-if ") or msg.startswith("/generate "):
        topic = message.split(" ", 1)[1]
        slug = topic.lower().replace(" ", "-")[:50]
        return {"intent": "generate", "topic": topic, "slug": slug, "title": f"What If: {topic}"}

    # AI Classification for natural language
    response = ask_ai(message, system=INTENT_SYSTEM_PROMPT)
    try:
        # Clean potential markdown from response
        clean_json = response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:-3].strip()
        elif clean_json.startswith("```"):
            clean_json = clean_json[3:-3].strip()
        
        result = json.loads(clean_json)
        return result
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse intent JSON: {response}")
        # Default to chat if parsing fails
        return {"intent": "chat"}
