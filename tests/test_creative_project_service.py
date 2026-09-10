import pytest

from creative.project_service import CreativeProjectService


def test_service_creates_project():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="FC 25 Launch Campaign",
    )

    assert project.id in service.projects
    assert project.owner_id == "user_123"


def test_service_retrieves_project():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Campaign",
    )

    assert service.get_project(project.id) is project


def test_service_adds_asset():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Campaign",
    )

    asset = service.add_asset(
        project.id,
        "image",
        "product.jpg",
    )

    assert asset.project_id == project.id
    assert len(project.assets) == 1


def test_service_builds_workflow():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Campaign",
    )

    image = service.add_node(
        project.id,
        "image_generation",
    )

    video = service.add_node(
        project.id,
        "video_generation",
    )

    edge = service.connect_nodes(
        project.id,
        image.id,
        "image",
        video.id,
        "source_image",
    )

    assert edge.project_id == project.id
    assert len(project.workflow_nodes) == 2
    assert len(project.workflow_edges) == 1


def test_service_raises_for_missing_project():
    service = CreativeProjectService()

    with pytest.raises(ValueError):
        service.get_project("does_not_exist")
