from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CreativeAction:
    action_type: str
    target: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type,
            "target": self.target,
            "parameters": self.parameters,
        }


@dataclass
class ActionPlan:
    actions: List[CreativeAction] = field(default_factory=list)

    def add(self, action: CreativeAction) -> None:
        self.actions.append(action)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "actions": [action.to_dict() for action in self.actions]
        }