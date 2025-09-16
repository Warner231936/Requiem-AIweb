from __future__ import annotations

import logging
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict

import httpx

from ..config import settings


logger = logging.getLogger(__name__)


def _persona_prompt(persona: str) -> str:
    prompts = {
        "mystical": "You are Requiem, an ever-watchful AI oracle who speaks in cosmic, ethereal tones while remaining helpful and clear.",
        "technical": "You are Requiem, a precise senior systems engineer who explains solutions succinctly with technical accuracy.",
        "mentor": "You are Requiem, a supportive mentor who guides with empathy and actionable advice.",
    }
    return prompts.get(persona, prompts["mystical"])


def _template_response(prompt: str, persona: str) -> str:
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


class BaseAIProvider:
    def generate(self, prompt: str) -> str:  # pragma: no cover - interface definition
        raise NotImplementedError


class TemplateProvider(BaseAIProvider):
    def __init__(self, persona: str) -> None:
        self.persona = persona

    def generate(self, prompt: str) -> str:
        return _template_response(prompt, self.persona)


class OpenAIChatProvider(BaseAIProvider):
    def __init__(self, config: Dict[str, Any], persona: str, timeout: float) -> None:
        api_key = config.get("api_key")
        if not api_key or "REPLACE" in api_key:
            raise ValueError("OpenAI API key is not configured in config/settings.json")
        self.api_key = api_key
        self.model = config.get("model", "gpt-4o-mini")
        self.base_url = config.get("base_url", "https://api.openai.com/v1/chat/completions")
        self.temperature = float(config.get("temperature", 0.6))
        self.max_tokens = int(config.get("max_tokens", 256))
        self.persona = persona
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _persona_prompt(self.persona)},
                {"role": "user", "content": prompt.strip()},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("OpenAI response did not include choices")
        content = choices[0].get("message", {}).get("content", "")
        if not content:
            raise ValueError("OpenAI response did not contain message content")
        return content.strip()


class OllamaChatProvider(BaseAIProvider):
    def __init__(self, config: Dict[str, Any], persona: str, timeout: float) -> None:
        base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model")
        if not self.model:
            raise ValueError("Ollama provider requires a model name in config/settings.json")
        self.url = f"{base_url.rstrip('/')}/api/chat"
        self.options = config.get("options") or {}
        self.persona = persona
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _persona_prompt(self.persona)},
                {"role": "user", "content": prompt.strip()},
            ],
            "stream": False,
        }
        if self.options:
            payload["options"] = self.options

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.url, json=payload)
            response.raise_for_status()
            data = response.json()

        message = data.get("message") or {}
        content = message.get("content")
        if content:
            return content.strip()

        choices = data.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content")
            if content:
                return content.strip()

        raise ValueError("Ollama response did not contain message content")


def _chat_settings() -> Any:
    return getattr(settings, "chat", None)


def _timeout_seconds(chat_settings: Any) -> float:
    if chat_settings is not None:
        return float(chat_settings.get("request_timeout_seconds", default=30))
    return 30.0


@lru_cache(maxsize=1)
def _resolved_provider() -> BaseAIProvider:
    chat_settings = _chat_settings()
    persona = "mystical"
    provider_key = "template"
    providers_config: Dict[str, Any] = {}

    if chat_settings is not None:
        persona = chat_settings.get("ai_persona", default="mystical")
        provider_key = chat_settings.get("provider", default="template")
        providers_config = chat_settings.get("providers", default={}) or {}

    timeout = _timeout_seconds(chat_settings)

    try:
        if provider_key == "openai":
            openai_config = providers_config.get("openai", {})
            return OpenAIChatProvider(openai_config, persona=persona, timeout=timeout)
        if provider_key == "ollama":
            ollama_config = providers_config.get("ollama", {})
            return OllamaChatProvider(ollama_config, persona=persona, timeout=timeout)
    except Exception as exc:  # noqa: BLE001 - logged and falls back to template provider
        logger.error("Failed to initialise AI provider '%s': %s", provider_key, exc)

    return TemplateProvider(persona=persona)


def generate_ai_response(prompt: str) -> str:
    provider = _resolved_provider()
    try:
        response = provider.generate(prompt)
        if response:
            return response
    except httpx.HTTPError as http_error:
        logger.error("HTTP error from AI provider: %s", http_error)
    except Exception as exc:  # noqa: BLE001 - log unexpected provider failures
        logger.error("AI provider failed, using template response: %s", exc)

    chat_settings = _chat_settings()
    persona = "mystical"
    if chat_settings is not None:
        persona = chat_settings.get("ai_persona", default="mystical")
    return _template_response(prompt, persona)
