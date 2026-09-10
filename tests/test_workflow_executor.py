import pytest

from creative.project_service import CreativeProjectService
from creative.workflow_executor import CreativeWorkflowExecutor


def test_executor_runs_linear_workflow():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="FC 25 Launch",
    )

    image = service.add_node(
        project.id,
        "image_generation",
    )

    video = service.add_node(
        project.id,
        "video_generation",
    )

    service.connect_nodes(
        project.id,
        image.id,
        "image",
        video.id,
        "source_image",
    )

    executor = CreativeWorkflowExecutor()
    result = executor.execute(project)

    assert result is project
    assert image.status == "completed"
    assert video.status == "completed"


def test_executor_runs_multiple_independent_nodes():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Campaign",
    )

    image = service.add_node(
        project.id,
        "image_generation",
    )

    copy = service.add_node(
        project.id,
        "copy_generation",
    )

    executor = CreativeWorkflowExecutor()
    executor.execute(project)

    assert image.status == "completed"
    assert copy.status == "completed"


def test_executor_detects_cycle():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Broken Workflow",
    )

    first = service.add_node(
        project.id,
        "image_generation",
    )

    second = service.add_node(
        project.id,
        "video_generation",
    )

    service.connect_nodes(
        project.id,
        first.id,
        "output",
        second.id,
        "input",
    )

    service.connect_nodes(
        project.id,
        second.id,
        "output",
        first.id,
        "input",
    )

    executor = CreativeWorkflowExecutor()

    with pytest.raises(ValueError):
        executor.execute(project)
