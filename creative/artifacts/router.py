from .base import ArtifactResult
from .website import WebsiteGenerator
from .game import GameGenerator
from .pdf import PDFGenerator


class ArtifactRouter:

    def route(
        self,
        artifact_type: str,
        **kwargs,
    ) -> ArtifactResult:

        artifact_type = artifact_type.lower().strip()

        if artifact_type in {"website", "site"}:
            return WebsiteGenerator().generate(**kwargs)

        if artifact_type == "game":
            return GameGenerator().generate(**kwargs)

        if artifact_type in {"pdf", "document"}:
            return PDFGenerator().generate(**kwargs)

        raise ValueError(
            f"Unsupported artifact type: {artifact_type}"
        )
