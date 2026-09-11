from typing import Any

from creative.project_service import CreativeProjectService


class CreativeEnvironment:
    """
    Runtime representation of Augeo's adaptive creative workspace.

    The environment describes what the user is creating,
    which assets/tools are relevant, and what the agent can do next.
    """

    def __init__(self, project_service=None):
        self.project_service = project_service or CreativeProjectService()

    def build(self, project_id: str) -> dict[str, Any]:
        project = self.project_service.get_project(project_id)

        medium = self._detect_medium(project)

        return {
            "project_id": project.id,
            "title": project.title,
            "status": project.status,
            "mode": medium,
            "assets": [asset.to_dict() for asset in project.assets],
            "workflow": [node.to_dict() for node in project.workflow_nodes],
            "connections": [
                edge.to_dict() for edge in project.workflow_edges
            ],
            "tools": self._tools_for(medium),
            "suggestions": self._suggestions_for(medium),
        }

    def _detect_medium(self, project) -> str:
        context = project.context

        if isinstance(context, dict):
            medium = context.get("medium")
            if medium:
                return medium

        for node in project.workflow_nodes:
            if node.type == "video_generation":
                return "video"
            if node.type == "image_generation":
                return "image"

        return "general"

    def _tools_for(self, medium: str) -> list[str]:
        tools = {
            "general": [
                "image_generation",
                "video_generation",
                "copy_generation",
            ],
            "image": [
                "image_generation",
                "image_editing",
                "typography",
                "layout",
                "background_removal",
            ],
            "video": [
                "storyboard",
                "image_generation",
                "video_generation",
                "timeline",
                "audio",
                "captions",
            ],
        }

        return tools.get(medium, tools["general"])

    def _suggestions_for(self, medium: str) -> list[str]:
        suggestions = {
            "general": [
                "Create an image",
                "Create a video",
                "Add an asset",
            ],
            "image": [
                "Generate variations",
                "Edit composition",
                "Change style",
                "Add copy",
            ],
            "video": [
                "Build storyboard",
                "Generate shots",
                "Edit timeline",
                "Add captions",
                "Add audio",
            ],
        }

        return suggestions.get(medium, suggestions["general"])