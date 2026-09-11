from typing import Any

from creative.project_service import CreativeProjectService
from creative.workflow_executor import CreativeWorkflowExecutor


class CreativeProjectBridge:
    """
    Connects the conversational creative experience to the
    persistent creative project/workflow system.
    """

    def __init__(
        self,
        project_service=None,
        executor=None,
    ):
        self.project_service = (
            project_service or CreativeProjectService()
        )
        self.executor = executor or CreativeWorkflowExecutor()

    def ensure_project(
        self,
        session,
        owner_id: str,
        title: str = "Untitled Creative Project",
        context: Any = None,
    ):
        if session.project_id:
            return self.project_service.get_project(
                session.project_id
            )

        project = self.project_service.create_project(
            owner_id=owner_id,
            title=title,
            context=context,
        )

        session.project_id = project.id

        return project

    def add_asset(
        self,
        session,
        owner_id: str,
        asset_type: str,
        source: str,
        metadata=None,
        title: str = "Creative Project",
        context=None,
    ):
        project = self.ensure_project(
            session=session,
            owner_id=owner_id,
            title=title,
            context=context,
        )

        return self.project_service.add_asset(
            project.id,
            asset_type,
            source,
            metadata=metadata,
        )

    def add_node(
        self,
        session,
        owner_id: str,
        node_type: str,
        inputs=None,
        configuration=None,
        title: str = "Creative Project",
        context=None,
    ):
        project = self.ensure_project(
            session=session,
            owner_id=owner_id,
            title=title,
            context=context,
        )

        return self.project_service.add_node(
            project.id,
            node_type,
            inputs=inputs,
            configuration=configuration,
        )

    def connect_nodes(
        self,
        session,
        source_node_id: str,
        source_output: str,
        target_node_id: str,
        target_input: str,
    ):
        if not session.project_id:
            raise ValueError(
                "Session is not attached to a creative project"
            )

        return self.project_service.connect_nodes(
            session.project_id,
            source_node_id,
            source_output,
            target_node_id,
            target_input,
        )

    def execute(self, session):
        if not session.project_id:
            raise ValueError(
                "Session is not attached to a creative project"
            )

        project = self.project_service.get_project(
            session.project_id
        )

        result = self.executor.execute(project)

        session.update_state(
            last_execution_status=result.status,
            last_project_snapshot=result.to_dict(),
        )

        return result