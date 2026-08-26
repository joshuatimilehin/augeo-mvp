from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Artifact:
    artifact_type: str
    path: str
    metadata: dict[str, Any]

    @property
    def exists(self) -> bool:
        return Path(self.path).exists()

    def as_dict(self) -> dict[str, Any]:
        return {
            "artifact_type": self.artifact_type,
            "path": self.path,
            "metadata": self.metadata,
            "exists": self.exists,
        }
