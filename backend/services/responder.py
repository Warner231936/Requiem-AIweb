from __future__ import annotations

from datetime import datetime

from ..config import settings


def generate_ai_response(prompt: str) -> str:
    """Generate a stylised AI response without external dependencies."""
    persona = settings.chat.get("ai_persona", default="mystical")
    timestamp = datetime.utcnow().strftime("%H:%M:%S UTC")
    base_response = (
        "I have heard your words and let them echo through the midnight halls. "
        "Here is what I perceive: "
    )
    closing = {
        "mystical": "Let the nebulae align with your intent.",
        "technical": "System resonance stabilised.",
        "mentor": "Your journey continues forward; I walk beside you.",
    }.get(persona, "Let the nebulae align with your intent.")

    return f"[{timestamp}] {base_response}{prompt.strip()} — {closing}"
