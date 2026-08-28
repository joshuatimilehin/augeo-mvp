from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from creative.capabilities import Capability, CapabilityRequest
from creative.artifacts import Artifact


class PDFCapability(Capability):
    name = "pdf"

    def execute(self, request: CapabilityRequest) -> dict:
        output_dir = Path("output/pdfs")
        output_dir.mkdir(parents=True, exist_ok=True)

        path = output_dir / "augeo_document.pdf"

        pdf = canvas.Canvas(str(path), pagesize=A4)

        width, height = A4

        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(60, height - 80, request.context.get(
            "title",
            "Augeo Document"
        ))

        pdf.setFont("Helvetica", 12)

        text = pdf.beginText(60, height - 120)
        text.setLeading(18)

        for line in request.instruction.splitlines():
            text.textLine(line)

        pdf.drawText(text)
        pdf.save()

        return Artifact(
            artifact_type="pdf",
            path=str(path),
            metadata={
                "format": "pdf",
                "pages": 1,
            },
        ).as_dict()
