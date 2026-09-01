import os
from typing import Optional, Dict, Any

class ProviderConfig:
    """Simple configuration accessor for provider API keys.

    Reads keys from environment variables and centralizes key names.
    """

    KEY_MAP = {
        "openai": "OPENAI_API_KEY",
        "ideogram": "IDEOGRAM_API_KEY",
        "higgsfield": "HIGGSFIELD_API_KEY",
    }

    @classmethod
    def get_key(cls, provider_name: str) -> Optional[str]:
        env = cls.KEY_MAP.get(provider_name.lower())
        if not env:
            return None
        return os.environ.get(env)


class ProviderInitializer:
    """Graceful provider initializer that returns None when credentials missing.

    Real provider clients should be created here when keys are available.
    For now this returns a lightweight dict describing the resolved state so
    higher-level code can decide to use a mock or fallback provider.
    """

    @staticmethod
    def init(provider_name: str) -> Dict[str, Any] | None:
        key = ProviderConfig.get_key(provider_name)
        if not key:
            return None
        # Placeholder: real client initialization would go here
        return {"provider": provider_name, "key_present": True}
