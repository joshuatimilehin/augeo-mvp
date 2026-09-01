from typing import Optional, List

from creative.context import CustomerContext
from creative.brand.profile import BrandProfile
from creative.reasoning.directions import (
    Direction,
    DirectionCandidate,
    ideate_directions,
)
from creative.reasoning.judgment import (
    CreativeJudge,
    CreativeJudgment,
    judge_direction,
)
from creative.reasoning.revision import CreativeRevisionEngine
from creative.reasoning.session import CreativeSession
from creative.reasoning.production import CreativeProductionSpec
from creative.reasoning.provider_router import CreativeProviderRouter
from creative.reasoning.quality_gate import CreativeQualityGate
from creative.reasoning.memory import record_learning, record_rejection


class CreativeDirector:
    """
    Augeo's creative-direction layer.

    Responsibilities:

        brief
            ?
        creative intent
            ?
        visual territories
            ?
        explicit taste judgment
            ?
        selected direction
            ?
        generation
            ?
        critique
            ?
        revision
            ?
        human approval
            ?
        learning
    """

    def __init__(self):
        self.judge = CreativeJudge()
        self.revision_engine = CreativeRevisionEngine()
        self.provider_router = CreativeProviderRouter()
        self.quality_gate = CreativeQualityGate()

    def start(
        self,
        context: CustomerContext,
        brief: str = "",
        brand: Optional[BrandProfile] = None,
    ) -> CreativeSession:

        return CreativeSession(
            context=context,
            brief=brief,
            # attach brand profile for later steps
            brand_profile=brand,
        )

    def ideate(self, session: CreativeSession, n: int = 3) -> List[DirectionCandidate]:
        """Generate `n` candidate directions and attach them to the session."""
        candidates = ideate_directions(session.context, brief=(session.brief or ""), n=n, brand=session.brand_profile)
        # run quality gate and mark rejects
        rejected = self.quality_gate.evaluate(candidates)
        for concept, reason in rejected.items():
            session.rejected_directions.append(concept)
            # persist rejection memory
            record_rejection({"concept": concept, "reason": reason, "brief": session.brief})

        # Filter out rejected candidates for initial judgment
        candidates = [c for c in candidates if c.direction.concept not in session.rejected_directions]
        session.propose_directions(candidates)
        return candidates

    def judge_directions(
        self,
        session: CreativeSession,
        candidates: list[DirectionCandidate],
    ) -> CreativeJudgment:

        session.directions = candidates

        # Use the explicit judge to evaluate and annotate candidates
        judgment = self.judge.judge(candidates, brand=session.brand_profile)

        session.judgment = judgment
        session.selected_direction = judgment.winner
        session.status = "direction_selected"

        # persist learning for the winner and rejected ones
        record_learning({
            "winner": judgment.winner,
            "score": judgment.score,
            "brief": session.brief,
        })
        for r in session.rejected_directions:
            record_rejection({"concept": r, "reason": "quality_gate_reject", "brief": session.brief})

        return judgment

    def create_production_spec(
        self,
        session: CreativeSession,
        deliverable: str,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None,
        variation_count: int = 1,
    ) -> CreativeProductionSpec:
        """Create a provider-agnostic production specification from the session state."""
        spec = CreativeProductionSpec(
            deliverable=deliverable,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            creative_direction=session.selected_direction,
            visual_references=[],
            product_assets=list(session.context.brand_name and [session.context.brand_name] or []),
            brand_constraints=[],
            prompt=None,
            variation_count=variation_count,
        )
        return spec

    def route_production(self, spec: CreativeProductionSpec, *, quality: Optional[str] = None, speed: Optional[str] = None, cost: Optional[str] = None) -> dict:
        return self.provider_router.route(spec, quality_requirement=quality, speed_requirement=speed, cost_requirement=cost)

    def review(self, session: CreativeSession) -> dict:
        """Return a structured review payload for UI or API consumption."""
        return {
            "status": session.status,
            "brief": session.brief,
            "proposed_directions": [c.direction.concept for c in session.proposed_directions],
            "selected_direction": session.selected_direction,
            "judgment": session.judgment and session.judgment.why,
            "revisions": [r.critique for r in session.revisions],
            "rejected": session.rejected_directions,
        }

    def request_changes(self, session: CreativeSession, *, critique: str, weak_areas: list[str]):
        """Create a revision plan from human critique and attach it to the session."""
        plan = self.revision_engine.create_revision(iteration=len(session.revisions) + 1, critique=critique, weak_areas=weak_areas)
        # Revision engine returns a RevisionPlan; append to session.revisions for audit
        session.revisions.append(plan)
        session.status = "changes_requested"
        return plan

    def apply_revision(self, session: CreativeSession, plan) -> None:
        """Apply a revision plan to the session. This is intentionally lightweight;
        callers should implement domain-specific application logic (e.g., regenerate directions).
        """
        session.revisions.append(plan)
        session.status = "revision"

    def approve_session(self, session: CreativeSession, note: str = "") -> None:
        session.approve(note)
        # persist final approval
        record_learning({"approved": session.selected_direction, "note": note, "brief": session.brief})

    def reject_session(self, session: CreativeSession, note: str = "") -> None:
        session.reject(note)
        # record rejection of the selected direction if any
        if session.selected_direction:
            record_rejection({"concept": session.selected_direction, "reason": note, "brief": session.brief})

    def revise(
        self,
        session: CreativeSession,
        *,
        critique: str,
        weak_areas: list[str],
    ):

        revision = self.revision_engine.create_revision(
            critique=critique,
            weak_areas=weak_areas,
            iteration=len(session.revisions) + 1,
        )

        session.revisions.append(revision)
        session.status = "revision"

        return revision
