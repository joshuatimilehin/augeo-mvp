from __future__ import annotations

from pathlib import Path

from creative.capabilities import Capability, CapabilityRequest
from creative.artifacts import Artifact


class GameCapability(Capability):
    name = "game"

    def execute(self, request: CapabilityRequest) -> dict:
        output_dir = Path("output/games") / "latest"
        output_dir.mkdir(parents=True, exist_ok=True)

        html = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Augeo Game</title>
    <style>
        body {
            margin: 0;
            background: #111;
            color: white;
            font-family: system-ui;
            display: grid;
            place-items: center;
            min-height: 100vh;
        }

        button {
            padding: 14px 22px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div>
        <h1>Augeo Game</h1>
        <p id="status">Ready.</p>
        <button onclick="play()">Play</button>
    </div>

    <script>
        function play() {
            document.getElementById("status").textContent =
                "Game started.";
        }
    </script>
</body>
</html>
"""

        path = output_dir / "index.html"
        path.write_text(html, encoding="utf-8")

        return Artifact(
            artifact_type="game",
            path=str(path),
            metadata={
                "format": "html",
                "runtime": "browser",
            },
        ).as_dict()
