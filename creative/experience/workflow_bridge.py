from creative.experience.actions import CreativeAction
from creative.workflow_executor import CreativeWorkflowExecutor


class CreativeActionWorkflowBridge:
    def __init__(self, project_service, workflow_executor=None):
        self.project_service = project_service
        self.workflow_executor = (
            workflow_executor
            or CreativeWorkflowExecutor()
        )

    def apply_action(self, project_id, action):
        if isinstance(action, dict):
            action = CreativeAction(
                action_type=action["action_type"],
                parameters=action.get("parameters", {}),
            )

        if action.action_type == "clarify":
            return {
                "status": "needs_clarification",
                "action": action,
            }

        if action.action_type == "create_image":
            node_type = "image_generation"
        elif action.action_type == "create_video":
            node_type = "video_generation"
        else:
            raise ValueError(
                f"Unsupported creative action: {action.action_type}"
            )

        node = self.project_service.add_node(
            project_id,
            node_type,
            inputs=action.parameters,
        )

        return {
            "status": "planned",
            "node_type": node_type,
            "node_id": node.id,
            "action": action,
        }

    def execute_project(self, project_id):
        project = self.project_service.get_project(project_id)

        if project is None:
            raise ValueError(
                f"Creative project not found: {project_id}"
            )

        return self.workflow_executor.execute(project)