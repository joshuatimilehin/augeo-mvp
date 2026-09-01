from typing import Dict, Optional, Any

from creative.reasoning.production import CreativeProductionSpec
from creative.provider_utils import ProviderConfig, ProviderInitializer


class CreativeProviderRouter:
    """Simple provider router deciding where to send production jobs.

    This is a deterministic, extensible router used before wiring real
    provider integrations. It returns a provider key and optional hints.
    """

    def __init__(self):
        # Example provider keys: 'ideogram', 'video_engine', 'llm', 'mock'
        self.mapping = {
            "static_image": "ideogram",
            "short_video": "video_engine",
            "long_video": "video_engine",
            "copy": "llm",
        }

    def route(
        self,
        spec: CreativeProductionSpec,
        quality_requirement: Optional[str] = None,
        speed_requirement: Optional[str] = None,
        cost_requirement: Optional[str] = None,
    ) -> Dict[str, Optional[str]]:
        deliverable = (spec.deliverable or "").lower()

        provider = self.mapping.get(deliverable, "mock")

        # honor explicit provider hints (capability routing)
        provider_hints = spec.provider_hints or []
        if any(h.startswith("preferred_tone:") for h in provider_hints):
            # prefer LLMs for nuanced tone instructions
            provider = "llm"

        hints = []
        if quality_requirement == "high":
            hints.append("use-high-quality-model")
        if speed_requirement == "fast":
            hints.append("low-latency-model")
        if cost_requirement == "low":
            hints.append("cost-optimized")

        # Provider-level adjustments already considered; now attempt init
        client = ProviderInitializer.init(provider)
        has_key = ProviderConfig.get_key(provider) is not None

        return {
            "provider": provider,
            "hints": ",".join(provider_hints + hints) if (provider_hints or hints) else None,
            "has_key": has_key,
            "client": client,
        }
