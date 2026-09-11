from creative.experience.actions import CreativeAction
from creative.project_service import CreativeProjectService
from creative.workflow_executor import CreativeWorkflowExecutor


class CreativeActionWorkflowBridge:
    """
    Converts high-level creative actions into executable project workflows.
    """

    ACTION_TO_NODE = {
        "create_image": "image_generation",
        "create_video": "video_generation",
        "create_copy": "copy_generation",
    }

    def __init__(
        self,
        project_service=None,
        workflow_executor=None,
    ):
        self.project_service = (
            project_service or CreativeProjectService()
        )
        self.workflow_executor = (
            workflow_executor or CreativeWorkflowExecutor()
        )

    def apply_action(self, project_id, action: CreativeAction):
        if action.action_type == "clarify":
            return {
                "status": "needs_clarification",
                "question": action.parameters.get(
                    "question",
                    "What would you like to create?",
                ),
            }

        node_type = self.ACTION_TO_NODE.get(action.action_type)

        if node_type is None:
            raise ValueError(
                f"Cannot map action to workflow node: "
                f"{action.action_type}"
            )

        node = self.project_service.add_node(
            project_id,
            node_type,
            configuration=action.parameters,
        )

        return {
            "status": "planned",
            "action_type": action.action_type,
            "node_id": node.id,
            "node_type": node.type,
        }

    def execute_project(self, project_id):
        project = self.project_service.get_project(project_id)

        self.workflow_executor.execute(project)

        return project
