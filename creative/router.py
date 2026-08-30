"""A stable, channel-neutral router for Augeo creative requests.

Channels (WhatsApp today, social tags tomorrow) only submit a request.  The
router owns classification, the brief, and the delivery contract so new
generators can be added without teaching customers new software.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CORE_CAPABILITIES = (
    "graphic_design",
    "ugc_video",
    "launch_video",
    "social_copy",
    "content_plan",
)


@dataclass(frozen=True)
class CreativeBrief:
    capability: str
    instruction: str
    channel: str = "social"
    brand: dict[str, Any] = field(default_factory=dict)
    assets: tuple[str, ...] = ()

    @property
    def subject(self) -> str:
        return self.instruction.strip()[:160] or "your product"


class CreativeRouter:
    """Returns one consistent result shape for every supported deliverable."""

    def create_brief(
        self,
        capability: str,
        instruction: str,
        context: dict[str, Any] | None = None,
    ) -> CreativeBrief:
        context = context or {}
        if capability not in CORE_CAPABILITIES:
            raise ValueError(f"Unsupported core creative capability: {capability}")
        assets = tuple(str(asset) for asset in context.get("assets", []) if asset)
        return CreativeBrief(
            capability=capability,
            instruction=instruction,
            channel=str(context.get("channel") or "social"),
            brand=dict(context.get("brand") or {}),
            assets=assets,
        )

    def route(self, brief: CreativeBrief) -> dict[str, Any]:
        if brief.capability == "graphic_design":
            return self._visual_intake(brief)
        if brief.capability == "ugc_video":
            return self._ugc_video(brief)
        if brief.capability == "launch_video":
            return self._launch_video_brief(brief)
        if brief.capability == "social_copy":
            return self._social_copy(brief)
        if brief.capability == "content_plan":
            return self._content_plan(brief)
        raise ValueError(f"No route configured for {brief.capability}")

    @staticmethod
    def _base(brief: CreativeBrief, deliverable: str, status: str) -> dict[str, Any]:
        return {
            "capability": brief.capability,
            "deliverable": deliverable,
            "status": status,
            "channel": brief.channel,
            "brand": brief.brand,
        }

    def _visual_intake(self, brief: CreativeBrief) -> dict[str, Any]:
        result = self._base(brief, "design", "needs_input")
        result.update({
            "message": "Send a product photo (or reference), the offer/price, and where it will be posted. I’ll turn that into the design brief and visual.",
            "required_inputs": ["product or reference image", "offer or price", "publishing channel"],
        })
        return result

    def _ugc_video(self, brief: CreativeBrief) -> dict[str, Any]:
        if not brief.assets:
            result = self._base(brief, "ugc_video", "needs_input")
            result.update({
                "message": "Send a clean product photo first. I’ll use it to make the UGC video look like your actual product, not a generic substitute.",
                "required_inputs": ["product or reference image"],
            })
            return result
        result = self._base(brief, "ugc_video", "ready")
        result["content"] = "\n".join([
            f"Hook (0–2s): ‘I didn’t expect {brief.subject} to be this useful.’",
            "Proof (2–8s): show the product in use and one specific result.",
            "Payoff (8–14s): explain the benefit in one honest sentence.",
            "Close (14–18s): ‘Comment INFO or send a DM for the details.’",
        ])
        return result

    def _launch_video_brief(self, brief: CreativeBrief) -> dict[str, Any]:
        result = self._base(brief, "launch_video_brief", "ready")
        result["content"] = "\n".join([
            "0–2s — Pattern break: bold product/offer reveal.",
            "2–7s — Problem: name the frustration in the buyer’s words.",
            "7–14s — Product proof: show it solving that problem.",
            "14–20s — Offer: price, availability, and one direct CTA.",
            "Format: vertical 9:16, captions on, product visible in the first second.",
        ])
        return result

    def _social_copy(self, brief: CreativeBrief) -> dict[str, Any]:
        result = self._base(brief, "caption", "ready")
        result["content"] = "\n".join([
            f"{brief.subject} — made for people who want the good stuff without the stress.",
            "Simple, useful, and ready when you are. Send a DM to order.",
        ])
        return result

    def _content_plan(self, brief: CreativeBrief) -> dict[str, Any]:
        result = self._base(brief, "five_day_content_plan", "ready")
        result["content"] = "\n".join([
            "Day 1: the customer problem.",
            "Day 2: a use case or customer story.",
            "Day 3: a 20-second how-to.",
            "Day 4: product proof or FAQ.",
            "Day 5: direct offer with one call to action.",
        ])
        return result
