from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class JobStatus(str, Enum):
    DRAFT = "draft"
    IDEATION = "ideation"
    PROPOSED = "proposed"
    DIRECTION_SELECTED = "direction_selected"
    REVISION = "revision"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    FINAL = "final"


class ApprovalState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    REJECTED = "rejected"


@dataclass
class MultimodalContext:
    """Unified context bundle for chat, references, media, and intent."""

    text: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    voice_notes: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    intent: Optional[str] = None
    summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_text(self, *entries: str) -> None:
        for entry in entries:
            if entry:
                self.text.append(entry)

    def add_image(self, *uris: str) -> None:
        for uri in uris:
            if uri:
                self.images.append(uri)

    def add_url(self, *urls: str) -> None:
        for url in urls:
            if url:
                self.urls.append(url)

    def add_voice_note(self, *entries: str) -> None:
        for entry in entries:
            if entry:
                self.voice_notes.append(entry)

    def add_video(self, *uris: str) -> None:
        for uri in uris:
            if uri:
                self.videos.append(uri)


@dataclass
class ReferenceSignal:
    """Reference intelligence: exact match, emotional inspiration, or style reference."""

    kind: str  # exact, emotional, inspiration, product-preservation
    source: str
    summary: str = ""
    notes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreativeMemoryProfile:
    """Broader memory than brand-only memory: person, taste, project, and audience context."""

    person_id: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    creative_taste: Dict[str, Any] = field(default_factory=dict)
    project_history: List[str] = field(default_factory=list)
    brands: List[str] = field(default_factory=list)
    audiences: List[str] = field(default_factory=list)
    learned_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelDecision:
    """Decision made by the system before a creative job enters generation."""

    primary_model: str = "astra-gpt-6"
    fallback_model: str = "claude-fable-5-1"
    task_type: str = "reasoning"
    rationale: str = "Primary reasoning brain for creative orchestration, fallback for recovery."
    quality_score: float = 0.0


class ModelRouter:
    """Simple routing layer: choose a model based on the job and desired quality profile."""

    def decide(
        self,
        job: "CreativeJob",
        *,
        quality: str = "balanced",
        latency: str = "normal",
        cost: str = "balanced",
    ) -> ModelDecision:
        primary_model = "astra-gpt-6"
        fallback_model = "claude-fable-5-1"

        if job.medium.lower() in {"video", "ugc", "launch_video"}:
            task_type = "video-planning"
        elif job.medium.lower() in {"image", "static_image"}:
            task_type = "image-planning"
        else:
            task_type = "reasoning"

        rationale = (
            "Astra GPT 6 is the primary planner and decision-maker for this creative job. "
            "Fable 5.1 remains the fallback for resilience and recovery."
        )

        if quality == "high":
            rationale += " High quality routing prioritizes the planning brain."
        if latency == "fast":
            rationale += " Fast routing prefers lower-latency fallback paths."
        if cost == "low":
            rationale += " Cost-aware routing keeps fallback economics in play."

        return ModelDecision(
            primary_model=primary_model,
            fallback_model=fallback_model,
            task_type=task_type,
            rationale=rationale,
            quality_score=0.92,
        )


@dataclass
class CreativeCritique:
    """Structured critique from the quality/evaluation loop."""

    summary: str
    strengths: List[str] = field(default_factory=list)
    weak_areas: List[str] = field(default_factory=list)
    recommended_changes: List[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class CreativeJob:
    """Canonical job abstraction for all creative production work."""

    intent: str = ""
    subject: str = ""
    audience: str = ""
    context: MultimodalContext = field(default_factory=MultimodalContext)
    desired_effect: str = ""
    medium: str = ""
    format: str = ""
    constraints: List[str] = field(default_factory=list)
    references: List[ReferenceSignal] = field(default_factory=list)
    creative_direction: Optional[str] = None
    production_plan: Optional[Dict[str, Any]] = None
    generation_requirements: Dict[str, Any] = field(default_factory=dict)
    approval_state: ApprovalState = ApprovalState.PENDING
    status: JobStatus = JobStatus.DRAFT
    revisions: List[CreativeCritique] = field(default_factory=list)
    memory: Optional[CreativeMemoryProfile] = None
    model_decision: Optional[ModelDecision] = None
    notes: List[str] = field(default_factory=list)

    def set_approval(self, approved: bool, note: str = "") -> None:
        if approved:
            self.approval_state = ApprovalState.APPROVED
            self.status = JobStatus.APPROVED
        else:
            self.approval_state = ApprovalState.CHANGES_REQUESTED
            self.status = JobStatus.CHANGES_REQUESTED
        if note:
            self.notes.append(note)

    def add_reference(self, kind: str, source: str, summary: str = "", **kwargs: Any) -> None:
        self.references.append(
            ReferenceSignal(
                kind=kind,
                source=source,
                summary=summary,
                notes=kwargs,
            )
        )

    def add_revision(self, critique: CreativeCritique) -> None:
        self.revisions.append(critique)
        self.status = JobStatus.REVISION

    def finalize(self) -> None:
        self.status = JobStatus.FINAL
        self.approval_state = ApprovalState.APPROVED


class CreativeOrchestrator:
    """Thin orchestration layer for the launch-ready creative flow."""

    def __init__(self, router: Optional[ModelRouter] = None):
        self.router = router or ModelRouter()

    def create_job(
        self,
        *,
        intent: str,
        subject: str,
        audience: str,
        context: Optional[MultimodalContext] = None,
        desired_effect: str,
        medium: str,
        format: str,
        constraints: Optional[List[str]] = None,
        references: Optional[List[ReferenceSignal]] = None,
        memory: Optional[CreativeMemoryProfile] = None,
    ) -> CreativeJob:
        job = CreativeJob(
            intent=intent,
            subject=subject,
            audience=audience,
            context=context or MultimodalContext(intent=intent),
            desired_effect=desired_effect,
            medium=medium,
            format=format,
            constraints=list(constraints or []),
            references=list(references or []),
            memory=memory,
        )
        job.model_decision = self.router.decide(job)
        return job

    def evaluate(self, job: CreativeJob, *, summary: str, weak_areas: List[str], recommended_changes: List[str], score: float) -> CreativeCritique:
        critique = CreativeCritique(
            summary=summary,
            weak_areas=list(weak_areas),
            recommended_changes=list(recommended_changes),
            score=float(score),
        )
        job.add_revision(critique)
        return critique
