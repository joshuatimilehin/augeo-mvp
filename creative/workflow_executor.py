from creative.project import CreativeProject
from creative.providers.registry import ProviderRegistry


class CreativeWorkflowExecutor:
    def __init__(self, provider_registry=None):
        self.registry = provider_registry or ProviderRegistry()

    def execute(self, project: CreativeProject):
        completed = set()
        outputs = {}

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

                if not all(
                    dependency in completed
                    for dependency in dependencies
                ):
                    continue

                inputs = dict(node.inputs)

                for edge in project.workflow_edges:
                    if edge.target_node_id != node.id:
                        continue

                    source_output = outputs.get(edge.source_node_id)

                    if source_output is not None:
                        inputs[edge.target_input] = source_output

                provider = self.registry.get(node.type)

                node.status = "running"

                result = provider.execute(node, inputs)

                node.outputs = result
                outputs[node.id] = result
                node.status = "completed"

                asset_type = result.get("type")
                source = result.get("source")

                if asset_type and source:
                    project.add_asset(
                        asset_type,
                        source,
                        {
                            "node_id": node.id,
                            "provider": result.get("provider"),
                        },
                    )

                completed.add(node.id)
                progressed = True

            if not progressed:
                raise ValueError(
                    "Workflow contains unresolved dependencies or a cycle"
                )

        return project
