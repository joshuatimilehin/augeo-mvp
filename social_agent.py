"""Public tag interface for Augeo's focused creative router.

The public product deliberately exposes only the creative workflows Augeo can
guide end-to-end today. Other experimental artifact modules remain internal.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from creative.router import CORE_CAPABILITIES, CreativeRouter
from creative.video import VideoGenerationError, build_video_service


CAPABILITIES = CORE_CAPABILITIES


@dataclass(frozen=True)
class SocialRequest:
    capability: str
    instruction: str


class SocialAgent:
    """Turns a tag or DM into one clear creative deliverable."""

    _PATTERNS = (
        ("launch_video", r"\b(launch video|brand film|brand video|product launch|launch reel|promo video|commercial video|ad film|film for my brand|fc 25 launch|game launch trailer)\b"),
        ("creative_direction", r"\b(anime matchday|matchday experience|fc 25|football launch trailer|anime opening|creative direction|reimagine this|make it anime|make something like|garfield|recreate some really cool episodes|old cartoon|cartoon episode|film, lol|maybe a film|make a film|make something cool|surprise me|creative concept|idea for a film|idea for a video)\b"),
        ("campaign_direction", r"\b(launch campaign|new product|product launch|social campaign|feature launch|brand campaign|motion graphic|launch day|new feature)\b"),
        ("brand_video", r"\b(video ad|brand ad|brand commercial|promo reel|product film|company film|business video|brand content)\b"),
        ("ugc_video", r"\b(ugc|creator script|reel script|tiktok script|video script)\b"),
        ("content_plan", r"\b(content plan|content calendar|content ideas|campaign)\b"),
        ("social_copy", r"\b(caption|copy|write a post|social post|educat|teach|explain)\b"),
        ("graphic_design", r"\b(create|make|generate|design).{0,30}\b(image|visual|graphic|poster|flyer|ad|advertisement|creative)\b"),
        ("graphic_design", r"\b(flyer|poster|graphic design|advertisement|brand visual|creative asset)\b"),
    )

    def classify(self, text: str) -> SocialRequest | None:
        instruction = re.sub(r"^\s*@?augeo[,:\s-]*", "", text or "", flags=re.I).strip()
        for capability, pattern in self._PATTERNS:
            if re.search(pattern, instruction, re.I):
                return SocialRequest(capability, instruction)
        return None

    def __init__(self, video_service=None) -> None:
        self.video_service = video_service or build_video_service()

    def execute(self, request: SocialRequest, context: dict[str, Any] | None = None) -> dict[str, Any]:
        router = CreativeRouter()
        brief = router.create_brief(request.capability, request.instruction, context)
        result = router.route(brief)
        if request.capability not in {"launch_video", "ugc_video"} or result["status"] != "ready":
            return result

        try:
            job = self.video_service.submit(
                self._video_prompt(brief, result["content"]),
                reference_url=brief.assets[0] if brief.assets else None,
            )
        except VideoGenerationError as exc:
            result.update({"status": "failed", "message": str(exc)})
            return result

        result["video"] = job
        if job["status"] == "needs_configuration":
            result["status"] = "needs_configuration"
            result["message"] = job["message"]
        else:
            result.update({
                "status": "submitted",
                "message": "Your launch video is rendering. Check the video status endpoint with this job ID.",
            })
        return result

    @staticmethod
    def _video_prompt(brief, storyboard: str) -> str:
        brand = brief.brand.get("business_name") or "the brand"
        return (
            f"Create an original vertical product launch video for {brand}. "
            f"Request: {brief.instruction}\n\nStoryboard:\n{storyboard}\n\n"
            "Use clean legible visual storytelling. Do not include third-party logos, "
            "copyrighted characters, or unverified claims."
        )
