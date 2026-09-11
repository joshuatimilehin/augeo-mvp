from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CreativeIntent:
    raw_request: str

    goal: Optional[str] = None
    medium: Optional[str] = None
    subject: Optional[str] = None
    audience: Optional[str] = None
    style: Optional[str] = None

    requested_actions: List[str] = field(default_factory=list)

    confidence: float = 0.0

    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_request": self.raw_request,
            "goal": self.goal,
            "medium": self.medium,
            "subject": self.subject,
            "audience": self.audience,
            "style": self.style,
            "requested_actions": self.requested_actions,
            "confidence": self.confidence,
            "context": self.context,
        }