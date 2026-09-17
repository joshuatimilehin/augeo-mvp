from creative.experience.actions import CreativeAction
from creative.experience.action_executor import CreativeActionExecutor
from creative.project_service import CreativeProjectService


def test_action_executor_creates_image_node():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Launch",
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
    assert project.workflow_nodes[0].type == "image_generation"


def test_action_executor_creates_video_node():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Launch",
    )

    executor = CreativeActionExecutor(service)

    result = executor.execute(
        project.id,
        CreativeAction(
            action_type="create_video",
            parameters={
                "style": "cinematic",
                "purpose": "launch",
            },
        ),
    )

    assert result["status"] == "planned"
    assert result["action_type"] == "create_video"
    assert result["node_type"] == "video_generation"
    assert len(project.workflow_nodes) == 1
    assert project.workflow_nodes[0].type == "video_generation"


def test_action_executor_rejects_unknown_action():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Launch",
    )

    executor = CreativeActionExecutor(service)

    try:
        executor.execute(
            project.id,
            CreativeAction(
                action_type="destroy_universe",
            ),
        )
    except ValueError as exc:
        assert "Unknown creative action" in str(exc)
    else:
        raise AssertionError(
            "Expected unknown action to raise ValueError"
        )