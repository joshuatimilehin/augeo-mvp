from creative.experience.director import CreativeDirector
from creative.experience.environment import CreativeEnvironment
from creative.experience.session import ExperienceSession
from creative.experience.workflow_bridge import CreativeActionWorkflowBridge
from creative.project_service import CreativeProjectService


class CreativeExperienceOrchestrator:
    def __init__(self, project_service=None):
        self.project_service = project_service or CreativeProjectService()
        self.director = CreativeDirector()
        self.environment = CreativeEnvironment(self.project_service)
        self.workflow_bridge = CreativeActionWorkflowBridge(
            project_service=self.project_service
        )

    def handle(self, project_or_message, message_or_session, session=None):
        """
        Supports both:

            handle(project_id, message, session)
            handle(message, session)

        The second form is the voice-first experience.
        """

        if session is None:
            project_id = None
            message = project_or_message
            session = message_or_session

            if not isinstance(session, ExperienceSession):
                raise TypeError(
                    "Expected ExperienceSession as second argument"
                )

            if session.project_id:
                project_id = session.project_id
            else:
                project = self.project_service.create_project(
                    owner_id=session.session_id,
                    title="Creative Session",
                )
                project_id = project.id
                session.project_id = project_id

        else:
            project_id = project_or_message
            message = message_or_session

            if not isinstance(session, ExperienceSession):
                raise TypeError(
                    "Expected ExperienceSession as third argument"
                )

            session.project_id = project_id

        direction = self.director.direct(
            message,
            session,
        )

        environment = self.environment.adapt(
            project_id,
            direction["intent"],
        )

        for action in direction["plan"]["actions"]:
            self.workflow_bridge.apply_action(
                project_id,
                action,
            )

        project = self.project_service.get_project(project_id)

        execution = self.workflow_bridge.execute_project(
            project_id
        )

        return {
            "message": message,
            "intent": direction["intent"],
            "plan": direction["plan"],
            "environment": environment,
            "project": project,
            "execution": execution,
        }
