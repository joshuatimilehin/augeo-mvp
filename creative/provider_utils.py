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
        "higgfield": "HIGGSFIELD_API_KEY",
        "runway": "RUNWAYML_API_SECRET",
        "seedance": "SEEDANCE_API_KEY",
    }

    @classmethod
    def get_key(cls, provider_name: str) -> Optional[str]:
        # lazy-load .env if present to ease local dev
        if not getattr(cls, "_dotenv_loaded", False):
            cls._dotenv_loaded = False
            cls._maybe_load_dotenv()

        env = cls.KEY_MAP.get(provider_name.lower())
        if not env:
            return None
        return os.environ.get(env)

    @classmethod
    def _maybe_load_dotenv(cls, path: Optional[str] = None) -> None:
        # Load a .env file from the repository root if present and not already loaded.
        if getattr(cls, "_dotenv_loaded", False):
            return
        p = path or (os.path.join(os.getcwd(), ".env"))
        if not os.path.exists(p):
            cls._dotenv_loaded = True
            return
        try:
            cls.load_dotenv(p)
        finally:
            cls._dotenv_loaded = True

    @classmethod
    def load_dotenv(cls, path: str) -> None:
        """Parse a simple .env file and set values into os.environ when not present.

        Supports lines like KEY=VALUE, ignores comments and blank lines.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and (os.environ.get(k) is None):
                        os.environ[k] = v
        except Exception:
            # don't fail loudly on dotenv parsing issues
            return


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

        provider_name = (provider_name or "").lower()

        # Attempt to initialize common SDKs if available. Fail gracefully.
        if provider_name in ("openai", "llm"):
            try:
                import openai

                # set key if available
                openai.api_key = key
                return {"provider": "openai", "client": "openai", "key_present": True}
            except Exception:
                # OpenAI SDK isn't installed or failed to import; return descriptor
                return {"provider": "openai", "client": "openai-import-failed", "key_present": True}

        if provider_name in ("ideogram", "image", "video_engine", "higgsfield", "higgfield", "runway", "seedance"):
            # Provider clients are intentionally lightweight descriptors until a real
            # SDK or adapter is required; they should fall back gracefully when keys are absent.
            return {"provider": provider_name, "client": "descriptor", "key_present": True}

        # Generic fallback descriptor for unknown providers
        return {"provider": provider_name, "client": "descriptor", "key_present": True}
