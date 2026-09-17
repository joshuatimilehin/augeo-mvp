from creative.experience.action_executor import (
    CreativeActionExecutor,
)
from creative.experience.director import CreativeDirector
from creative.experience.environment import CreativeEnvironment
from creative.experience.session import ExperienceSession
from creative.project_service import CreativeProjectService
from creative.workflow_executor import CreativeWorkflowExecutor


class CreativeExperienceOrchestrator:
    """
    Top-level creative experience coordinator.

    Human request
        ?
    Director
        ?
    Action plan
        ?
    Workflow nodes
        ?
    Workflow execution
        ?
    Project result
    """

    def __init__(
        self,
        project_service=None,
        workflow_executor=None,
    ):
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

        self.workflow_executor = (
            workflow_executor
            or CreativeWorkflowExecutor()
        )

    def handle(
        self,
        project_or_message,
        message_or_session,
        session=None,
    ):
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

        else:
            project_id = project_or_message
            message = message_or_session

            if not isinstance(session, ExperienceSession):
                raise TypeError(
                    "session must be an ExperienceSession"
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

        planned_actions = []

        for action in direction["plan"]["actions"]:
            result = self.action_executor.execute(
                project_id,
                action,
            )

            planned_actions.append(result)

        project = self.project_service.get_project(
            project_id
        )

        project = self.workflow_executor.execute(
            project
        )

        return {
            "message": message,
            "intent": direction["intent"],
            "plan": direction["plan"],
            "environment": environment,
            "actions": planned_actions,
            "project": project,
        }
