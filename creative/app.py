from creative.experience.orchestrator import CreativeExperienceOrchestrator
from creative.experience.session import ExperienceSession


class CreativeApp:
    """
    Application boundary for Augeo's new creative experience.

    Transport layers such as HTTP, WhatsApp, or a future UI
    should call this boundary rather than reaching directly
    into generation, providers, or workflow internals.
    """

    def __init__(self, project_service=None):
        self.experience = CreativeExperienceOrchestrator(
            project_service=project_service
        )

    def handle(self, message: str, session_id: str):
        session = ExperienceSession(session_id=session_id)

        return self.experience.handle(
            message,
            session,
        )