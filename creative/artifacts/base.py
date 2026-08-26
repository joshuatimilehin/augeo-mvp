from dataclasses import dataclass, field
from typing import Any


@dataclass
class ArtifactResult:
    artifact_type: str
    success: bool
    output_path: str | None = None
    content: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
