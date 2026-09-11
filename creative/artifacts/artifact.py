from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _now():
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CreativeArtifact:
    project_id: str
    artifact_type: str
    source: str
    id: str = field(
        default_factory=lambda: f"artifact_{uuid4().hex}"
    )
    status: str = "created"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "artifact_type": self.artifact_type,
            "source": self.source,
            "status": self.status,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }