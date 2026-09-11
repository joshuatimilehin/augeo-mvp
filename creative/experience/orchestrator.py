from creative.experience.director import CreativeDirector
from creative.experience.environment import CreativeEnvironment
from creative.experience.session import ExperienceSession
from creative.project_service import CreativeProjectService


class CreativeExperienceOrchestrator:
    def __init__(self, project_service=None):
        self.project_service = project_service or CreativeProjectService()
        self.director = CreativeDirector()
        self.environment = CreativeEnvironment(self.project_service)

    def handle(self, project_id, message, session):
        direction = self.director.direct(message, session)

        environment = self.environment.adapt(
            project_id,
            direction["intent"],
        )

        return {
            "message": message,
            "intent": direction["intent"],
            "plan": direction["plan"],
            "environment": environment,
        }