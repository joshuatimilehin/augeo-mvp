from dataclasses import dataclass, field
from typing import Optional, List

from creative.context import CustomerContext
from creative.reasoning.directions import DirectionCandidate
from creative.reasoning.judgment import CreativeJudgment
from creative.reasoning.revision import Revision
from creative.brand.profile import BrandProfile


@dataclass
class CreativeSession:
    context: CustomerContext
    brief: Optional[str] = None
    # Session status states: ideation -> proposed -> direction_selected -> revision -> changes_requested -> approved
    status: str = "ideation"

    # Directions proposed in the ideation phase
    proposed_directions: List[DirectionCandidate] = field(default_factory=list)

    # Selected direction concept string
    selected_direction: Optional[str] = None
    judgment: Optional[CreativeJudgment] = None

    # Revision history stores Revision or RevisionPlan objects
    revisions: List[Revision] = field(default_factory=list)

    # Rejected directions (concept names)
    rejected_directions: List[str] = field(default_factory=list)

    # Optional attached brand profile for the session
    brand_profile: Optional[BrandProfile] = None

    human_approved: bool = False
    approval_note: Optional[str] = None

    def approve(self, note: str = "") -> None:
        self.human_approved = True
        self.approval_note = note
        self.status = "approved"

    def reject(self, note: str = "") -> None:
        self.human_approved = False
        self.approval_note = note
        self.status = "changes_requested"


    def propose_directions(self, candidates: list[DirectionCandidate]) -> None:
        self.proposed_directions = candidates
        self.status = "proposed"


    def select_direction(self, concept: str, judgment: Optional[CreativeJudgment] = None) -> None:
        # ensure the selected concept exists in proposed directions unless it's being selected after revisions
        proposed_concepts = [c.direction.concept for c in self.proposed_directions]
        if proposed_concepts and concept not in proposed_concepts:
            raise ValueError(f"Cannot select direction '{concept}'; not in proposed directions")

        self.selected_direction = concept
        if judgment:
            self.judgment = judgment
        self.status = "direction_selected"


    def request_changes(self, critique: str, weak_areas: list[str]) -> None:
        self.status = "changes_requested"
        # record last critique as a lightweight revision record
        revision = Revision(iteration=len(self.revisions) + 1, critique=critique, weak_areas=list(weak_areas), changes=[])
        self.revisions.append(revision)


    def add_revision(self, revision: Revision) -> Revision:
        self.revisions.append(revision)
        self.status = "revision"
        return revision

    def attach_brand_profile(self, profile: BrandProfile) -> None:
        self.brand_profile = profile

    def current_revision(self) -> Optional[Revision]:
        if not self.revisions:
            return None
        return self.revisions[-1]
