from creative.experience.actions import CreativeAction
from creative.project_service import CreativeProjectService


class CreativeActionExecutor:
    """
    Canonical boundary between creative direction
    and project workflow construction.

    This layer does NOT execute providers.

    It translates:
        CreativeAction
            ↓
        WorkflowNode

    Actual execution belongs to CreativeWorkflowExecutor.
    """

    ACTION_TO_NODE = {
        "create_image": "image_generation",
        "create_video": "video_generation",
        "create_copy": "copy_generation",
    }

    def __init__(self, project_service=None):
        self.project_service = (
            project_service
            or CreativeProjectService()
        )

    def execute(self, project_id, action):
        if isinstance(action, dict):
            action = CreativeAction(
                action_type=action["action_type"],
                parameters=action.get("parameters", {}),
            )

        if not isinstance(action, CreativeAction):
            raise TypeError(
                "action must be a CreativeAction or dict"
            )

        if action.action_type == "clarify":
            return {
                "status": "needs_clarification",
                "action": action.to_dict(),
            }

        node_type = self.ACTION_TO_NODE.get(
            action.action_type
        )

        if node_type is None:
            raise ValueError(
                f"Unknown creative action: "
                f"{action.action_type}"
            )

        node = self.project_service.add_node(
            project_id=project_id,
            node_type=node_type,
            inputs=action.parameters,
        )

        return {
            "status": "planned",
            "action_type": action.action_type,
            "node_type": node_type,
            "node_id": node.id,
        }