from pathlib import Path
from .base import ArtifactResult


class WebsiteGenerator:

    def generate(
        self,
        html: str,
        output_path: str = "output/website.html",
    ) -> ArtifactResult:

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            html,
            encoding="utf-8",
        )

        return ArtifactResult(
            artifact_type="website",
            success=True,
            output_path=str(path),
        )
