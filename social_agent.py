"""The lightweight command layer behind Augeo's tag-to-create experience."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from creative.agent import AugeoAgent
from creative.capabilities.defaults import build_registry

CAPABILITIES = ("caption", "ugc", "teach", "plan", "image", "flyer", "website", "pdf", "game", "code")


@dataclass(frozen=True)
class SocialRequest:
    capability: str
    instruction: str


class SocialAgent:
    """Route natural, tag-friendly social requests into compact outputs."""

    _PATTERNS = (
        ("ugc", r"\b(ugc|creator script|reel script|tiktok script|video script)\b"),
        ("teach", r"\b(explain|teach|educat|how do i|how to|pedagog)\b"),
        ("plan", r"\b(content plan|calendar|content ideas|campaign)\b"),
        ("caption", r"\b(caption|copy|write a post|social post)\b"),
        ("image", r"\b(create|make|generate|design).{0,30}\b(image|visual|graphic|poster)\b"),
        ("flyer", r"\b(flyer|ad|advertisement)\b"),
        ("website", r"\b(website|site|landing page|home page|homepage)\b"),
        ("pdf", r"\b(pdf|catalogue|catalog|document)\b"),
        ("game", r"\b(game|mini game)\b"),
        ("code", r"\b(code|python|javascript|typescript|function|method|class|script|snippet|program)\b"),
    )

    def classify(self, text: str) -> SocialRequest | None:
        cleaned = re.sub(r"^\s*@?augeo[,:\s-]*", "", text or "", flags=re.I).strip()
        for capability, pattern in self._PATTERNS:
            if re.search(pattern, cleaned, re.I):
                return SocialRequest(capability, cleaned)
        return None

    def execute(self, request: SocialRequest, context: dict[str, Any] | None = None) -> dict[str, Any]:
        subject = self._subject(request.instruction)
        if request.capability == "caption":
            return self._result("caption", [f"{subject} — made for people who want the good stuff without the stress.", "Simple, useful, and ready when you are. Send a DM to order."])
        if request.capability == "ugc":
            return self._result("ugc", [f"Hook (0–2s): ‘I didn’t expect {subject} to be this useful.’", "Show: one clear before/after or the product in use.", "Say: ‘Here’s what made me keep using it…’ Then name one real benefit.", "Close: ‘Want the details? Comment ‘INFO’ or send a DM.’"])
        if request.capability == "teach":
            return self._result("educational_post", [f"{subject}, simply:", "1. Start with the one outcome your customer wants.", "2. Show the smallest action they can take today.", "3. End with one clear next step — not five."])
        if request.capability == "plan":
            return self._result("content_plan", [f"Day 1: the problem {subject} solves.", "Day 2: a real use case or customer story.", "Day 3: a 20-second how-to.", "Day 4: product proof / FAQ.", "Day 5: direct offer with one call to action."])
        if request.capability in {"image", "flyer"}:
            return {"type": "creative_brief", "capability": request.capability, "status": "needs_asset", "message": "Send the product photo (or describe the subject), price, and delivery details. I’ll make the visual from there.", "instruction": request.instruction}
        if request.capability == "code":
            return {
                "type": "code",
                "capability": "code",
                "status": "ready",
                "content": self._generate_code(request.instruction),
                "message": "Here is a working starter snippet for your request.",
            }
        if request.capability in {"website", "pdf", "game"}:
            agent = AugeoAgent(registry=build_registry())
            result = agent.handle(request.instruction, context=context or {})
            output = result.output
            return {
                "type": "artifact",
                "capability": request.capability,
                "status": "ready",
                "artifact_type": output.get("artifact_type"),
                "path": output.get("path"),
                "metadata": output.get("metadata", {}),
                "message": f"Built your {request.capability} artifact.",
            }
        raise ValueError("Unsupported Augeo capability")

    @staticmethod
    def _subject(instruction: str) -> str:
        subject = re.sub(r"\b(please|can you|create|make|write|a|an|the|caption|ugc|script|post|about|for)\b", "", instruction, flags=re.I)
        subject = re.sub(r"\s+", " ", subject).strip(" .,:-‘’\"")
        return subject[:90] or "your product"

    @staticmethod
    def _generate_code(instruction: str) -> str:
        cleaned = instruction.strip()
        lowered = cleaned.lower()

        if "sum" in lowered and "two" in lowered and "number" in lowered:
            return (
                "def sum_two_numbers(a, b):\n"
                "    return a + b\n\n\n"
                "print(sum_two_numbers(3, 5))\n"
            )

        if "reverse" in lowered and "string" in lowered:
            return (
                "def reverse_string(text):\n"
                "    return text[::-1]\n\n\n"
                "print(reverse_string('augeo'))\n"
            )

        if "hello" in lowered or "greet" in lowered:
            return (
                "def greet(name):\n"
                "    return f'Hello, {name}!\'\n\n\n"
                "print(greet('Augeo'))\n"
            )

        return (
            "def solve_task(input_value):\n"
            "    # Replace this with your real logic\n"
            "    return input_value\n\n\n"
            "print(solve_task('your value'))\n"
        )

    @staticmethod
    def _result(kind: str, lines: list[str]) -> dict[str, Any]:
        return {"type": kind, "status": "ready", "content": "\n".join(lines)}
