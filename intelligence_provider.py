from typing import Dict, Any
import os
from abc import ABC, abstractmethod
from config import ANTHROPIC_API_KEY, INTELLIGENCE_DEFAULT_MODEL


class IntelligenceProvider(ABC):
    """Abstract interface for intelligence/reasoning providers."""

    @abstractmethod
    def analyze(self, prompt: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Perform reasoning/analysis given a prompt and optional context.

        Returns a dict with at least:
        - `text`: str (the response)
        - `metadata`: dict (provider-specific details)
        """
        raise NotImplementedError()


class MockIntelligenceProvider(IntelligenceProvider):
    def analyze(self, prompt: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # Deterministic mock for tests/local development
        response_text = f"(mock-fable) I read the prompt: {prompt[:200]}"
        return {"text": response_text, "metadata": {"model": "mock-fable"}}


class AnthropicFableProvider(IntelligenceProvider):
    """Minimal Anthropic/Fable wrapper. Does NOT require a real key for import.

    Note: network calls are performed only when `ANTHROPIC_API_KEY` is present.
    """

    def __init__(self, model: str = None, api_key: str | None = None):
        self.model = model or INTELLIGENCE_DEFAULT_MODEL
        self.api_key = api_key or ANTHROPIC_API_KEY

    def analyze(self, prompt: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # If no API key is configured, behave deterministically like the mock
        if not self.api_key:
            return {"text": f"(mocked-fable) {prompt[:200]}", "metadata": {"model": self.model, "mock": True}}

        # Minimal HTTP call scaffold to Anthropic (pseudo code — adapt to actual client)
        try:
            import requests
            url = "https://api.anthropic.com/v1/complete"
            headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}
            payload = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": 800,
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            # The exact shape depends on Anthropic's response format; adapt as needed
            text = data.get('completion') or data.get('text') or data.get('output') or ''
            return {"text": text, "metadata": data}
        except Exception as e:
            # Fail gracefully to mock-like response
            return {"text": f"(fallback-fable) {prompt[:200]}", "metadata": {"error": str(e), "model": self.model}}


def get_intelligence_provider(name: str | None = None) -> IntelligenceProvider:
    """Factory to obtain an IntelligenceProvider. The `name` can be 'anthropic', 'mock', etc.

    Defaults to Anthropic Fable (or mock when no key present).
    """
    name = (name or '').lower()
    # Default to Anthropic/Fable but return mock if no API key
    if name in ('mock', 'fake', 'test'):
        return MockIntelligenceProvider()
    if name in ('anthropic', 'fable', 'claude') or not name:
        # Use Anthropic provider but it will fallback to mock behavior if key missing
        return AnthropicFableProvider()
    # Unknown provider — fallback to mock
    return MockIntelligenceProvider()
