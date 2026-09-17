from dataclasses import dataclass, field
from typing import Any


@dataclass
class CreativeAction:
    action_type: str
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type,
            "parameters": self.parameters,
        }


@dataclass
class ActionPlan:
    actions: list[CreativeAction] = field(default_factory=list)

    def add(
        self,
        action_type: str,
        parameters: dict[str, Any] | None = None,
    ) -> CreativeAction:
        action = CreativeAction(
            action_type=action_type,
            parameters=parameters or {},
        )

        self.actions.append(action)

        return action

    def to_dict(self) -> dict[str, Any]:
        return {
            "actions": [
                action.to_dict()
                for action in self.actions
            ]
        }


