from pathlib import Path
from .base import ArtifactResult


class PDFGenerator:

    def generate(
        self,
        content: str,
        output_path: str = "output/document.pdf",
    ) -> ArtifactResult:

        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        document = SimpleDocTemplate(
            str(path),
            pagesize=A4,
        )

        styles = getSampleStyleSheet()

        story = [
            Paragraph(
                paragraph,
                styles["BodyText"],
            )
            for paragraph in content.split("\n")
            if paragraph.strip()
        ]

        document.build(story)

        return ArtifactResult(
            artifact_type="pdf",
            success=True,
            output_path=str(path),
        )
