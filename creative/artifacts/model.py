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
        normalized_path = Path(self.path).as_posix()

        return {
            "artifact_type": self.artifact_type,
            "path": normalized_path,
            "metadata": self.metadata,
            "exists": self.exists,
        }
