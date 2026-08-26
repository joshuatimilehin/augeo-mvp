from pathlib import Path
from .base import ArtifactResult


class GameGenerator:

    def generate(
        self,
        html: str,
        output_path: str = "output/game.html",
    ) -> ArtifactResult:

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            html,
            encoding="utf-8",
        )

        return ArtifactResult(
            artifact_type="game",
            success=True,
            output_path=str(path),
        )
