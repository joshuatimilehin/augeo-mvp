from creative.experience.actions import CreativeAction
from creative.experience.workflow_bridge import (
    CreativeActionWorkflowBridge,
)
from creative.project_service import CreativeProjectService


def test_action_becomes_image_workflow_node():
    service = CreativeProjectService()
    project = service.create_project(
        owner_id="user_123",
        title="Launch",
    )

    bridge = CreativeActionWorkflowBridge(
        project_service=service,
    )

    result = bridge.apply_action(
        project.id,
        CreativeAction(
            action_type="create_image",
            parameters={
                "style": "premium",
            },
        ),
    )

    assert result["status"] == "planned"
    assert result["node_type"] == "image_generation"
    assert len(project.workflow_nodes) == 1


def test_action_becomes_video_workflow_node():
    service = CreativeProjectService()
    project = service.create_project(
        owner_id="user_123",
        title="Launch",
    )

    bridge = CreativeActionWorkflowBridge(
        project_service=service,
    )

    result = bridge.apply_action(
        project.id,
        CreativeAction(
            action_type="create_video",
            parameters={
                "style": "cinematic",
            },
        ),
    )

    assert result["node_type"] == "video_generation"


def test_clarification_does_not_create_node():
    service = CreativeProjectService()
    project = service.create_project(
        owner_id="user_123",
        title="Launch",
    )

    bridge = CreativeActionWorkflowBridge(
        project_service=service,
    )

    result = bridge.apply_action(
        project.id,
        CreativeAction(
            action_type="clarify",
            parameters={
                "question": "What should I create?",
            },
        ),
    )

    assert result["status"] == "needs_clarification"
    assert len(project.workflow_nodes) == 0


def test_bridge_executes_project():
    service = CreativeProjectService()
    project = service.create_project(
        owner_id="user_123",
        title="Launch",
    )

    bridge = CreativeActionWorkflowBridge(
        project_service=service,
    )

    bridge.apply_action(
        project.id,
        CreativeAction(
            action_type="create_image",
            parameters={
                "style": "premium",
            },
        ),
    )

    result = bridge.execute_project(project.id)

    assert result is project
    assert project.workflow_nodes[0].status == "completed"
    assert project.workflow_nodes[0].outputs["type"] == "image"
