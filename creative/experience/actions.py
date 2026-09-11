from dataclasses import dataclass, field
from typing import Any


@dataclass
class CreativeAction:
    action_type: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionPlan:
    actions: list[CreativeAction] = field(default_factory=list)

    def add(self, action: CreativeAction) -> None:
        self.actions.append(action)

    def to_dict(self) -> dict[str, Any]:
        return {
            "actions": [
                {
                    "action_type": action.action_type,
                    "parameters": action.parameters,
                }
                for action in self.actions
            ]
        }


class CreativeActionExecutor:
    def __init__(self, project_service):
        self.project_service = project_service

    def execute(self, project_id: str, action: CreativeAction):
        project = self.project_service.get_project(project_id)

        if action.action_type == "create_image":
            node = self.project_service.add_node(
                project_id,
                "image_generation",
                configuration=action.parameters,
            )
            return {
                "action": action.action_type,
                "status": "completed",
                "node_id": node.id,
            }

        if action.action_type == "create_video":
            node = self.project_service.add_node(
                project_id,
                "video_generation",
                configuration=action.parameters,
            )
            return {
                "action": action.action_type,
                "status": "completed",
                "node_id": node.id,
            }

        if action.action_type == "create_copy":
            node = self.project_service.add_node(
                project_id,
                "copy_generation",
                configuration=action.parameters,
            )
            return {
                "action": action.action_type,
                "status": "completed",
                "node_id": node.id,
            }

        if action.action_type == "clarify":
            return {
                "action": action.action_type,
                "status": "needs_clarification",
                "question": action.parameters.get(
                    "question",
                    "What would you like to create?",
                ),
            }

        raise ValueError(
            f"Unsupported creative action: {action.action_type}"
        )
