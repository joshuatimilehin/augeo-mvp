from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExperienceSession:
    session_id: str
    project_id: Optional[str] = None

    messages: List[Dict[str, str]] = field(default_factory=list)

    current_intent: Optional[Dict[str, Any]] = None

    state: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({
            "role": role,
            "content": content,
        })

    def set_intent(self, intent: Dict[str, Any]) -> None:
        self.current_intent = intent

    def update_state(self, **values: Any) -> None:
        self.state.update(values)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "project_id": self.project_id,
            "messages": list(self.messages),
            "current_intent": self.current_intent,
            "state": dict(self.state),
        }