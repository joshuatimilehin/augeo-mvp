from typing import Dict, Any
import os
from abc import ABC, abstractmethod
from config import ANTHROPIC_API_KEY, INTELLIGENCE_DEFAULT_MODEL, INTELLIGENCE_FALLBACK_MODEL


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


class AstraGPT6Provider(IntelligenceProvider):
    """Primary brain for Augeo. Falls back to Fable if the Astra call fails."""

    def __init__(self, model: str = None, fallback_model: str | None = None, api_key: str | None = None):
        self.model = model or INTELLIGENCE_DEFAULT_MODEL
        self.fallback_model = fallback_model or INTELLIGENCE_FALLBACK_MODEL
        self.api_key = api_key or os.getenv("ASTRA_API_KEY") or os.getenv("OPENAI_API_KEY")

    def analyze(self, prompt: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.api_key:
            return AnthropicFableProvider(model=self.fallback_model, api_key=ANTHROPIC_API_KEY).analyze(prompt, context)

        try:
            import requests
            url = os.getenv("ASTRA_API_URL", "https://api.astra.ai/v1/chat/completions")
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            text = data.get('choices', [{}])[0].get('message', {}).get('content') or data.get('text') or data.get('completion') or ''
            return {"text": text, "metadata": {"model": self.model, "provider": "astra-gpt-6"}}
        except Exception as e:
            fallback_provider = AnthropicFableProvider(model=self.fallback_model, api_key=ANTHROPIC_API_KEY)
            fallback_resp = fallback_provider.analyze(prompt, context)
            return {
                "text": fallback_resp.get("text") or f"(fallback-astra-to-fable) {prompt[:200]}",
                "metadata": {"error": str(e), "model": self.fallback_model, "fallback": True, "provider": "fable-5.1"},
            }


class AnthropicFableProvider(IntelligenceProvider):
    """Minimal Anthropic/Fable wrapper. Does NOT require a real key for import.

    Note: network calls are performed only when `ANTHROPIC_API_KEY` is present.
    """

    def __init__(self, model: str = None, api_key: str | None = None):
        self.model = model or INTELLIGENCE_FALLBACK_MODEL
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
            return {"text": text, "metadata": {"model": self.model, "provider": "fable-5.1"}}
        except Exception as e:
            # Fail gracefully to mock-like response
            return {"text": f"(fallback-fable) {prompt[:200]}", "metadata": {"error": str(e), "model": self.model}}


def get_intelligence_provider(name: str | None = None) -> IntelligenceProvider:
    """Factory to obtain an IntelligenceProvider.

    Defaults to Astra GPT 6, with Fable 5.1 as the fallback model.
    """
    name = (name or '').lower()
    if name in ('mock', 'fake', 'test'):
        return MockIntelligenceProvider()
    if name in ('astra', 'astra-gpt', 'astra-gpt-6', 'primary', 'brain') or not name:
        return AstraGPT6Provider()
    if name in ('anthropic', 'fable', 'claude', 'fallback', 'fable-5-1', 'claude-fable-5-1'):
        return AnthropicFableProvider(model=INTELLIGENCE_FALLBACK_MODEL)
    return MockIntelligenceProvider()
