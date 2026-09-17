from creative.experience.action_executor import (
    CreativeActionExecutor,
)
from creative.experience.director import CreativeDirector
from creative.experience.environment import CreativeEnvironment
from creative.experience.session import ExperienceSession
from creative.project_service import CreativeProjectService


class CreativeExperienceOrchestrator:
    """
    Top-level creative experience coordinator.

    Responsibilities:

        Human request
            ↓
        Director
            ↓
        Action plan
            ↓
        Action executor
            ↓
        Project workflow

    It does NOT directly execute providers.
    """

    def __init__(self, project_service=None):
        self.project_service = (
            project_service
            or CreativeProjectService()
        )

        self.director = CreativeDirector()

        self.environment = CreativeEnvironment(
            self.project_service
        )

        self.action_executor = CreativeActionExecutor(
            project_service=self.project_service
        )

    def handle(
        self,
        project_or_message,
        message_or_session,
        session=None,
    ):
        # Short form:
        #
        # handle(message, session)
        #
        # Used by CreativeApp.

        if session is None:
            project_id = None
            message = project_or_message
            session = message_or_session

            if not isinstance(session, ExperienceSession):
                raise TypeError(
                    "session must be an ExperienceSession"
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

        # Explicit project form:
        #
        # handle(project_id, message, session)

        else:
            project_id = project_or_message
            message = message_or_session

            if not isinstance(session, ExperienceSession):
                raise TypeError(
                    "session must be an ExperienceSession"
                )

            session.project_id = project_id

        # -------------------------------------------------
        # 1. Understand the human request.
        # -------------------------------------------------

        direction = self.director.direct(
            message,
            session,
        )

        # -------------------------------------------------
        # 2. Adapt the creative environment.
        # -------------------------------------------------

        environment = self.environment.adapt(
            project_id,
            direction["intent"],
        )

        # -------------------------------------------------
        # 3. Translate direction into workflow nodes.
        # -------------------------------------------------

        planned_actions = []

        for action in direction["plan"]["actions"]:
            result = self.action_executor.execute(
                project_id,
                action,
            )

            planned_actions.append(result)

        # -------------------------------------------------
        # 4. Retrieve the updated project.
        #
        # IMPORTANT:
        # We do not execute providers here.
        # The workflow executor owns execution.
        # -------------------------------------------------

        project = self.project_service.get_project(
            project_id
        )

        return {
            "message": message,
            "intent": direction["intent"],
            "plan": direction["plan"],
            "environment": environment,
            "actions": planned_actions,
            "project": project,
        }
