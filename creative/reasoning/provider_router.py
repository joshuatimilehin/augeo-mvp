from typing import Dict, Optional, Any

from creative.reasoning.production import CreativeProductionSpec
from creative.provider_utils import ProviderConfig, ProviderInitializer


class CreativeProviderRouter:
    """Simple provider router deciding where to send production jobs.

    This is a deterministic, extensible router used before wiring real
    provider integrations. It returns a provider key and optional hints.
    """

    def __init__(self):
        self.mapping = {
            "static_image": ["ideogram", "higgsfield", "mock"],
            "short_video": ["runway", "seedance", "openai", "higgsfield", "mock"],
            "long_video": ["runway", "seedance", "openai", "higgsfield", "mock"],
            "ugc_video": ["runway", "seedance", "openai", "higgsfield", "mock"],
            "launch_video": ["runway", "seedance", "openai", "higgsfield", "mock"],
            "copy": ["llm", "mock"],
        }

    def route(
        self,
        spec: CreativeProductionSpec,
        quality_requirement: Optional[str] = None,
        speed_requirement: Optional[str] = None,
        cost_requirement: Optional[str] = None,
    ) -> Dict[str, Optional[str]]:
        deliverable = (spec.deliverable or "").lower()
        provider_hints = spec.provider_hints or []
        candidates = self.mapping.get(deliverable, ["mock"])

        # honor explicit provider hints (capability routing)
        if any(h.startswith("preferred_tone:") for h in provider_hints):
            candidates = ["llm", *[p for p in candidates if p != "llm"]]

        provider = candidates[0]
        for candidate in candidates:
            if ProviderConfig.get_key(candidate) is not None or candidate == "mock":
                provider = candidate
                break

        hints = []
        if quality_requirement == "high":
            hints.append("use-high-quality-model")
        if speed_requirement == "fast":
            hints.append("low-latency-model")
        if cost_requirement == "low":
            hints.append("cost-optimized")

        client = ProviderInitializer.init(provider)
        has_key = ProviderConfig.get_key(provider) is not None

        return {
            "provider": provider,
            "fallbacks": [p for p in candidates if p != provider],
            "hints": ",".join(provider_hints + hints) if (provider_hints or hints) else None,
            "has_key": has_key,
            "client": client,
        }
