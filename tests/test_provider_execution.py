from creative.project_service import CreativeProjectService
from creative.workflow_executor import CreativeWorkflowExecutor


def test_executor_produces_node_outputs():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Launch Campaign",
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
    executor.execute(project)

    assert image.outputs["type"] == "image"
    assert image.outputs["provider"] == "mock"

    assert video.outputs["type"] == "video"
    assert video.outputs["provider"] == "mock"


def test_executor_passes_previous_output_forward():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Video Campaign",
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
    executor.execute(project)

    assert video.outputs is not None
