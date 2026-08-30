from __future__ import annotations

from dataclasses import dataclass, field, field
from typing import Any


@dataclass
class AudioPlan:
    required: bool
    mode: str
    voice_style: str | None = None
    rationale: str = ""
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def needs_audio(self) -> bool:
        """Backward-compatible semantic alias."""
        return self.required

    @property
    def audio_type(self) -> str | None:
        """Backward-compatible alias for integrations using audio_type."""
        if self.mode == "none":
            return None
        if self.mode in {"ugc_voice", "voiceover"}:
            return "voiceover"
        return self.mode


class AudioIntelligence:
    """Decides whether audio should be part of a creative deliverable."""

    def analyze(
        self,
        business: str,
        product: str,
        objective: str,
        content_type: str,
        context: dict[str, Any] | None = None,
    ) -> AudioPlan:
        content = content_type.lower()
        objective_lower = objective.lower()
        combined = f"{content} {objective_lower}"

        base_context = {
            "business": business,
            "product": product,
            "objective": objective,
            "content_type": content_type,
            **(context or {}),
        }

        # UGC gets a distinct mode because the voice should behave
        # like a creator speaking naturally, not like an advert narrator.
        if "ugc" in combined:
            return AudioPlan(
                required=True,
                mode="ugc_voice",
                voice_style="natural, conversational, authentic social-media creator",
                rationale="UGC content benefits from a human-sounding spoken delivery.",
                context=context,
            )

        # Launch/commercial video gets conventional narration.
        if any(
            phrase in combined
            for phrase in (
                "launch video",
                "product launch",
                "promo video",
                "commercial video",
                "campaign video",
                "brand video",
            )
        ):
            return AudioPlan(
    required=True,
    mode="voiceover",
    voice_style="polished, confident commercial narrator",
    rationale="A launch video benefits from structured narration.",
    context=context,
)

        # Static visual deliverables do not require audio.
        if any(
            phrase in combined
            for phrase in (
                "graphic_design",
                "graphic design",
                "poster",
                "flyer",
                "static",
                "image",
                "product poster",
            )
        ):
            return AudioPlan(
    required=False,
    mode="none",
    voice_style=None,
    rationale="Static creative does not require audio.",
    context=context,
)

        # Conservative default: don't invent an audio requirement.
        return AudioPlan(
            required=False,
            mode="none",
            rationale=(
                "Audio is not clearly required by the requested "
                "creative format."
            ),
            suggested_voice_direction=None,
            context=base_context,
        )
