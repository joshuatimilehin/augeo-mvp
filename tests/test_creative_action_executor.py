from creative.experience.action_executor import CreativeActionExecutor
from creative.experience.actions import CreativeAction
from creative.project_service import CreativeProjectService


def test_action_executor_turns_action_into_workflow_node():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Launch Campaign",
    )

    executor = CreativeActionExecutor(service)

    result = executor.execute(
        project.id,
        CreativeAction(
            action_type="create_image",
            parameters={
                "style": "premium",
                "purpose": "launch",
            },
        ),
    )

    assert result["status"] == "planned"
    assert result["action_type"] == "create_image"
    assert result["node_type"] == "image_generation"

    assert len(project.workflow_nodes) == 1

    node = project.workflow_nodes[0]

    assert node.type == "image_generation"
    assert node.status == "pending"