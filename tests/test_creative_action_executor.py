from creative.experience.action_executor import CreativeActionExecutor
from creative.project_service import CreativeProjectService
from creative.workflow_executor import CreativeWorkflowExecutor


def test_action_executor_turns_plan_into_workflow():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Launch Campaign",
    )

    executor = CreativeActionExecutor(
        CreativeWorkflowExecutor()
    )

    results = executor.execute(
        project,
        [
            {
                "action_type": "create_image",
            }
        ],
    )

    assert len(results) == 1
    assert results[0]["action_type"] == "create_image"
    assert results[0]["node_type"] == "image_generation"

    assert project.workflow_nodes[0].status == "completed"