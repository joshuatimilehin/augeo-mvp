from creative.project import CreativeProject


class CreativeProjectService:
    def __init__(self):
        self.projects: dict[str, CreativeProject] = {}

    def create_project(self, owner_id, title, context=None):
        project = CreativeProject(
            owner_id=owner_id,
            title=title,
            context=context,
        )
        self.projects[project.id] = project
        return project

    def get_project(self, project_id):
        try:
            return self.projects[project_id]
        except KeyError:
            raise ValueError(
                f"Creative project not found: {project_id}"
            )

    def add_asset(
        self,
        project_id,
        asset_type,
        source,
        metadata=None,
    ):
        return self.get_project(project_id).add_asset(
            asset_type=asset_type,
            source=source,
            metadata=metadata,
        )

    def add_node(
        self,
        project_id,
        node_type,
        inputs=None,
        configuration=None,
    ):
        return self.get_project(project_id).add_node(
            node_type=node_type,
            inputs=inputs,
            configuration=configuration,
        )

    def connect_nodes(
        self,
        project_id,
        source_node_id,
        source_output,
        target_node_id,
        target_input,
    ):
        return self.get_project(project_id).connect(
            source_node_id=source_node_id,
            source_output=source_output,
            target_node_id=target_node_id,
            target_input=target_input,
        )

    def serialize_project(self, project_id):
        return self.get_project(project_id).to_dict()
