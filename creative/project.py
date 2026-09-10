from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


@dataclass
class CreativeAsset:
    type: str
    source: str
    project_id: str
    id: str = field(default_factory=lambda: _id("asset"))
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowNode:
    type: str
    project_id: str
    inputs: dict[str, Any] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: _id("node"))
    status: str = "pending"
    outputs: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowEdge:
    project_id: str
    source_node_id: str
    source_output: str
    target_node_id: str
    target_input: str
    id: str = field(default_factory=lambda: _id("edge"))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CreativeProject:
    owner_id: str
    title: str
    context: Any = None
    id: str = field(default_factory=lambda: _id("project"))
    status: str = "active"
    assets: list[CreativeAsset] = field(default_factory=list)
    directions: list[Any] = field(default_factory=list)
    workflow_nodes: list[WorkflowNode] = field(default_factory=list)
    workflow_edges: list[WorkflowEdge] = field(default_factory=list)
    jobs: list[Any] = field(default_factory=list)
    revisions: list[Any] = field(default_factory=list)
    approvals: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def add_asset(
        self,
        asset_type: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> CreativeAsset:
        asset = CreativeAsset(
            type=asset_type,
            source=source,
            project_id=self.id,
            metadata=metadata or {},
        )
        self.assets.append(asset)
        self.updated_at = _now()
        return asset

    def add_node(
        self,
        node_type: str,
        inputs: dict[str, Any] | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> WorkflowNode:
        node = WorkflowNode(
            type=node_type,
            project_id=self.id,
            inputs=inputs or {},
            configuration=configuration or {},
        )
        self.workflow_nodes.append(node)
        self.updated_at = _now()
        return node

    def connect(
        self,
        source_node_id: str,
        source_output: str,
        target_node_id: str,
        target_input: str,
    ) -> WorkflowEdge:
        edge = WorkflowEdge(
            project_id=self.id,
            source_node_id=source_node_id,
            source_output=source_output,
            target_node_id=target_node_id,
            target_input=target_input,
        )
        self.workflow_edges.append(edge)
        self.updated_at = _now()
        return edge

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "title": self.title,
            "status": self.status,
            "context": (
                self.context.to_dict()
                if hasattr(self.context, "to_dict")
                else self.context
            ),
            "assets": [asset.to_dict() for asset in self.assets],
            "directions": self.directions,
            "workflow_nodes": [
                node.to_dict() for node in self.workflow_nodes
            ],
            "workflow_edges": [
                edge.to_dict() for edge in self.workflow_edges
            ],
            "jobs": self.jobs,
            "revisions": self.revisions,
            "approvals": self.approvals,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }