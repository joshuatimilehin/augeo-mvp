from creative.experience.environment import CreativeEnvironment
from creative.project_service import CreativeProjectService


def test_environment_builds_general_workspace():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Launch Campaign",
    )

    environment = CreativeEnvironment(service)
    result = environment.build(project.id)

    assert result["project_id"] == project.id
    assert result["mode"] == "general"
    assert "image_generation" in result["tools"]
    assert "video_generation" in result["tools"]


def test_environment_adapts_to_video_project():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Launch Video",
    )

    service.add_node(
        project.id,
        "video_generation",
    )

    environment = CreativeEnvironment(service)
    result = environment.build(project.id)

    assert result["mode"] == "video"
    assert "storyboard" in result["tools"]
    assert "timeline" in result["tools"]
    assert "video_generation" in result["tools"]


def test_environment_adapts_to_image_project():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Product Visual",
    )

    service.add_node(
        project.id,
        "image_generation",
    )

    environment = CreativeEnvironment(service)
    result = environment.build(project.id)

    assert result["mode"] == "image"
    assert "image_generation" in result["tools"]
    assert "layout" in result["tools"]