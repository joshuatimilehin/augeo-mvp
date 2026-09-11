from creative.project import CreativeProject


class CreativeWorkflowExecutor:
    def execute(self, project: CreativeProject):
        completed = set()

        while len(completed) < len(project.workflow_nodes):
            progressed = False

            for node in project.workflow_nodes:
                if node.id in completed:
                    continue

                dependencies = [
                    edge.source_node_id
                    for edge in project.workflow_edges
                    if edge.target_node_id == node.id
                ]

                if not all(dep in completed for dep in dependencies):
                    continue

                node.status = "completed"
                completed.add(node.id)
                progressed = True

            if not progressed:
                raise ValueError(
                    "Workflow contains unresolved dependencies or a cycle"
                )

        return project
