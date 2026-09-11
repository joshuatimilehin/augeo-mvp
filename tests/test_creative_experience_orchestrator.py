from creative.experience.orchestrator import CreativeExperienceOrchestrator
from creative.experience.session import ExperienceSession
from creative.project_service import CreativeProjectService


def test_experience_turn_adapts_workspace():
    service = CreativeProjectService()

    project = service.create_project(
        owner_id="user_123",
        title="Product Launch",
    )

    orchestrator = CreativeExperienceOrchestrator(service)
    session = ExperienceSession(session_id="session_123")

    result = orchestrator.handle(
        project.id,
        "Create a cinematic launch video",
        session,
    )

    assert result["intent"]["medium"] == "video"
    assert result["environment"]["mode"] == "video"
    assert "video_generation" in result["environment"]["tools"]
    assert "storyboard" in result["environment"]["tools"]