from dataclasses import dataclass, field


@dataclass
class MediaPlan:
    formats: list[str] = field(default_factory=list)
    objective: str = ""
    rationale: list[str] = field(default_factory=list)


class MediaPlanner:
    def plan(
        self,
        business: str,
        objective: str,
        audience: str,
        requested_format: str | None = None,
    ) -> MediaPlan:
        text = f"{objective} {requested_format or ''}".lower()

        formats: list[str] = []
        rationale: list[str] = []

        if "ugc" in text:
            formats.extend(["video", "voice"])
            rationale.append("UGC benefits from human-style video and spoken delivery.")
        elif any(word in text for word in ["launch", "campaign", "product"]):
            formats.extend(["image", "video"])
            rationale.append("A product campaign benefits from both a hero visual and motion.")
        else:
            formats.append("image")
            rationale.append("A static visual is the simplest starting point for this objective.")

        if "voice" in text or "voiceover" in text:
            if "voice" not in formats:
                formats.append("voice")

        if "poster" in text or "flyer" in text:
            formats = ["image"]

        return MediaPlan(
            formats=list(dict.fromkeys(formats)),
            objective=objective,
            rationale=rationale,
        )
