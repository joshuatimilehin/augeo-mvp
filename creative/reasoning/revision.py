from dataclasses import dataclass


@dataclass
class Revision:
    iteration: int
    critique: str
    weak_areas: list[str]
    changes: list[str]


@dataclass
class RevisionPlan:
    iteration: int
    critique: str
    weak_areas: list[str]
    changes: list[str]


def create_revision(
    iteration: int,
    critique: str,
    weak_areas: list[str],
) -> Revision:
    changes = [
        f"Strengthen {area}." for area in weak_areas
    ]

    return Revision(
        iteration=iteration,
        critique=critique,
        weak_areas=list(weak_areas),
        changes=changes,
    )


class CreativeRevisionEngine:
    """Small wrapper to provide a revision engine with a `create_revision` method."""

    def create_revision(
        self,
        *,
        iteration: int,
        critique: str,
        weak_areas: list[str],
    ) -> Revision:
        # Convert vague critique into concrete change steps
        plan_steps: list[str] = []

        mapping = {
            "distinctiveness": "Introduce a distinct visual hook that contrasts the category conventions (e.g. unusual prop, local collaborator, or contrasting color).",
            "composition": "Change framing: try asymmetrical composition, negative space, or closer crops to emphasize the product.",
            "emotional point of view": "Adjust the narrative to highlight a specific emotional arc (aspiration, nostalgia, rebellion).",
            "typography": "Switch to a display type that signals premium vs. approachable depending on brand voice.",
            "color": "Shift palette to a bolder accent or desaturated background depending on emotional goal.",
            "imagery": "Replace staged stock with authentic context shots or vice versa to improve believability.",
            "production complexity": "Reduce complexity by limiting set elements, using natural light, or simplifying wardrobe choices.",
        }

        for area in weak_areas:
            key = area.lower()
            found = False
            for k, v in mapping.items():
                if k in key:
                    plan_steps.append(v)
                    found = True
                    break
            if not found:
                plan_steps.append(f"Address {area}: translate critique into a focused adjustment.")

        if not plan_steps:
            plan_steps.append("Refine composition and strengthen the emotional point of view.")

        # Create a Revision that lists the concrete changes
        revision = create_revision(iteration=iteration, critique=critique, weak_areas=weak_areas)

        # Attach a simple plan object (RevisionPlan) as an informal field by returning it
        # alongside the Revision if callers expect it; for backwards compatibility,
        # return the Revision and the plan steps tuple.
        revision_plan = RevisionPlan(
            iteration=iteration,
            critique=critique,
            weak_areas=list(weak_areas),
            changes=plan_steps,
        )

        # For callers expecting a single object, return the RevisionPlan; director
        # currently treats this as a revision record.
        return revision_plan
