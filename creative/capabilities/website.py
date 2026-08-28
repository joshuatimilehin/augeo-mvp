from __future__ import annotations

from pathlib import Path
from creative.capabilities import Capability, CapabilityRequest
from creative.artifacts import Artifact


class WebsiteCapability(Capability):
    name = "website"

    def execute(self, request: CapabilityRequest) -> dict:
        output_dir = Path("output/websites") / "latest"
        output_dir.mkdir(parents=True, exist_ok=True)

        html = f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{request.context.get("title", "Augeo Website")}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <main>
        <h1>{request.context.get("title", "Augeo Website")}</h1>
        <p>{request.instruction}</p>
    </main>

    <script src="script.js"></script>
</body>
</html>
"""

        css = """
body {
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    font-family: system-ui, sans-serif;
}

main {
    max-width: 720px;
    padding: 48px;
}
"""

        js = """
console.log("Built by Augeo");
"""

        (output_dir / "index.html").write_text(html, encoding="utf-8")
        (output_dir / "style.css").write_text(css, encoding="utf-8")
        (output_dir / "script.js").write_text(js, encoding="utf-8")

        return Artifact(
            artifact_type="website",
            path=str(output_dir),
            metadata={
                "files": [
                    "index.html",
                    "style.css",
                    "script.js",
                ]
            },
        ).as_dict()
