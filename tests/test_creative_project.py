from creative.project import CreativeProject


def test_project_can_be_created():
    project = CreativeProject(
        owner_id="user_123",
        title="Luxury Handbag Campaign",
    )

    assert project.id.startswith("project_")
    assert project.status == "active"
    assert project.assets == []
    assert project.workflow_nodes == []


def test_project_can_attach_assets():
    project = CreativeProject(
        owner_id="user_123",
        title="Campaign",
    )

    asset = project.add_asset(
        asset_type="image",
        source="product.jpg",
    )

    assert asset.project_id == project.id
    assert asset.type == "image"
    assert len(project.assets) == 1


def test_project_can_create_workflow_nodes():
    project = CreativeProject(
        owner_id="user_123",
        title="Campaign",
    )

    image = project.add_node("image_generation")
    video = project.add_node("video_generation")

    assert image.project_id == project.id
    assert video.project_id == project.id
    assert len(project.workflow_nodes) == 2


def test_project_can_connect_workflow_nodes():
    project = CreativeProject(
        owner_id="user_123",
        title="Campaign",
    )

    image = project.add_node("image_generation")
    video = project.add_node("video_generation")

    edge = project.connect(
        source_node_id=image.id,
        source_output="image",
        target_node_id=video.id,
        target_input="source_image",
    )

    assert edge.project_id == project.id
    assert edge.source_node_id == image.id
    assert edge.target_node_id == video.id


def test_project_serializes():
    project = CreativeProject(
        owner_id="user_123",
        title="Campaign",
    )

    project.add_asset("image", "product.jpg")
    project.add_node("image_generation")

    data = project.to_dict()

    assert data["id"] == project.id
    assert data["title"] == "Campaign"
    assert len(data["assets"]) == 1
    assert len(data["workflow_nodes"]) == 1