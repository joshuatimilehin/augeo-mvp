from creative.experience.project_bridge import CreativeProjectBridge
from creative.experience.session import ExperienceSession


def test_bridge_creates_project_for_session():
    session = ExperienceSession(
        session_id="session_123"
    )

    bridge = CreativeProjectBridge()

    project = bridge.ensure_project(
        session=session,
        owner_id="user_123",
        title="Launch Campaign",
    )

    assert session.project_id == project.id
    assert project.title == "Launch Campaign"


def test_bridge_reuses_existing_project():
    session = ExperienceSession(
        session_id="session_123"
    )

    bridge = CreativeProjectBridge()

    first = bridge.ensure_project(
        session=session,
        owner_id="user_123",
    )

    second = bridge.ensure_project(
        session=session,
        owner_id="user_123",
    )

    assert first is second


def test_bridge_adds_asset():
    session = ExperienceSession(
        session_id="session_123"
    )

    bridge = CreativeProjectBridge()

    asset = bridge.add_asset(
        session=session,
        owner_id="user_123",
        asset_type="image",
        source="product.jpg",
    )

    assert asset.type == "image"
    assert session.project_id is not None


def test_bridge_adds_workflow_node():
    session = ExperienceSession(
        session_id="session_123"
    )

    bridge = CreativeProjectBridge()

    node = bridge.add_node(
        session=session,
        owner_id="user_123",
        node_type="image_generation",
    )

    assert node.type == "image_generation"
    assert session.project_id is not None


def test_bridge_executes_project():
    session = ExperienceSession(
        session_id="session_123"
    )

    bridge = CreativeProjectBridge()

    node = bridge.add_node(
        session=session,
        owner_id="user_123",
        node_type="image_generation",
    )

    project = bridge.execute(session)

    assert project.workflow_nodes[0].status == "completed"
    assert node.outputs["type"] == "image"