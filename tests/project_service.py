from creative.project import CreativeProject


class CreativeProjectService:
    """
    Application-level service for creating and mutating creative projects.

    Keeps project orchestration separate from the domain models so that
    WhatsApp, web, iMessage, voice, and future interfaces can all use
    the same project operations.
    """

    def __init__(self):
        self.projects: dict[str, CreativeProject] = {}

    def create_project(
        self,
        owner_id: str,
        title: str,
        context=None,
    ) -> CreativeProject:

        project = CreativeProject(
            owner_id=owner_id,
            title=title,
            context=context,
        )

        self.projects[project.id] = project
        return project

    def get_project(
        self,
        project_id: str,
    ) -> CreativeProject:

        try:
            return self.projects[project_id]
        except KeyError:
            raise ValueError(
                f"Creative project not found: {project_id}"
            )

    def add_asset(
        self,
        project_id: str,
        asset_type: str,
        source: str,
        metadata: dict | None = None,
    ):

        project = self.get_project(project_id)

        return project.add_asset(
            asset_type=asset_type,
            source=source,
            metadata=metadata,
        )

    def add_node(
        self,
        project_id: str,
        node_type: str,
        inputs: dict | None = None,
        configuration: dict | None = None,
    ):

        project = self.get_project(project_id)

        return project.add_node(
            node_type=node_type,
            inputs=inputs,
            configuration=configuration,
        )

    def connect_nodes(
        self,
        project_id: str,
        source_node_id: str,
        source_output: str,
        target_node_id: str,
        target_input: str,
    ):

        project = self.get_project(project_id)

        return project.connect(
            source_node_id=source_node_id,
            source_output=source_output,
            target_node_id=target_node_id,
            target_input=target_input,
        )

    def serialize_project(
        self,
        project_id: str,
    ) -> dict:

        return self.get_project(project_id).to_dict()