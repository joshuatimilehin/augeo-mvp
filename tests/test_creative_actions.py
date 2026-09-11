from creative.experience.actions import (
    CreativeAction,
    CreativeActionExecutor,
)
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

    assert result["status"] == "completed"
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
            },
        ),
    )

    assert result["status"] == "completed"
    assert project.workflow_nodes[0].type == "video_generation"


def test_action_executor_rejects_unknown_action():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Launch",
    )

    executor = CreativeActionExecutor(service)

    import pytest

    with pytest.raises(ValueError):
        executor.execute(
            project.id,
            CreativeAction(
                action_type="do_something_random",
                parameters={},
            ),
        )