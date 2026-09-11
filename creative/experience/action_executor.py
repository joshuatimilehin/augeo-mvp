class CreativeActionExecutor:

    def __init__(self, workflow_executor):
        self.workflow_executor = workflow_executor

    def execute(self, project, actions):
        results = []

        for action in actions:
            action_type = action.get("action_type")

            if action_type == "create_image":
                node_type = "image_generation"

            elif action_type == "create_video":
                node_type = "video_generation"

            elif action_type == "create_copy":
                node_type = "copy_generation"

            else:
                raise ValueError(
                    f"Unsupported creative action: {action_type}"
                )

            node = next(
                (
                    node
                    for node in project.workflow_nodes
                    if node.type == node_type
                    and node.status == "pending"
                ),
                None,
            )

            if node is None:
                node = project.add_node(node_type)

            results.append({
                "action_type": action_type,
                "node_id": node.id,
                "node_type": node.type,
            })

        self.workflow_executor.execute(project)

        return results