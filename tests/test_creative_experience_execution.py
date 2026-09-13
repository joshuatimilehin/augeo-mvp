from creative.experience.orchestrator import CreativeExperienceOrchestrator
from creative.experience.session import ExperienceSession


def test_voice_request_creates_and_executes_project():
    orchestrator = CreativeExperienceOrchestrator()

    session = ExperienceSession(
        session_id="execution-test"
    )

    result = orchestrator.handle(
        "Create a premium product launch visual",
        session,
    )

    assert result["intent"]["medium"] == "image"
    assert result["intent"]["style"] == "premium"

    assert "project" in result
    assert "execution" in result

    project = result["project"]

    assert project.workflow_nodes
    assert any(
        node.status == "completed"
        for node in project.workflow_nodes
    )