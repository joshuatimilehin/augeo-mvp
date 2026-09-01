from creative.context import CustomerContext
from creative.reasoning import (
    CreativeDirector,
    DirectionCandidate,
    create_direction,
)


def context():
    return CustomerContext(
        category="fashion",
        subcategory="luxury",
        product_name="Luxury Black Leather Handbag",
        product_description="Premium black leather handbag",
        price="?85,000",
        brand_name="Augeo Test Brand",
        audience="young professionals",
        location="Lagos, Nigeria",
        language="english",
        visual_style="luxury-editorial",
    )


def candidate(name, score):
    direction = create_direction(
        concept=name,
        visual_thesis="Editorial luxury with strong visual contrast.",
        emotional_goal="Desire and aspiration.",
        audience_effect="Make the product feel worth owning.",
        composition="Hero product with controlled negative space.",
        lighting="Directional premium studio lighting.",
        typography="Minimal premium typography.",
        color="Black, warm neutrals and restrained highlights.",
        imagery="Photorealistic commercial product photography.",
        differentiation="Strong editorial art direction.",
        rationale="It creates a recognisable visual point of view.",
        confidence=0.9,
    )

    return DirectionCandidate(
        direction=direction,
        strengths=["Clear visual identity"],
        risks=["Requires disciplined execution"],
        distinctiveness=score,
        fit=score,
        taste_score=score,
    )


def test_director_can_start_session():
    director = CreativeDirector()
    session = director.start(
        context(),
        brief="Create a premium campaign direction.",
    )

    assert session.status == "ideation"


def test_director_makes_explicit_judgment():
    director = CreativeDirector()
    session = director.start(context())

    judgment = director.judge_directions(
        session,
        [
            candidate("Safe Commerce", 0.55),
            candidate("Editorial Desire", 0.92),
            candidate("Street Luxury", 0.74),
        ],
    )

    assert judgment.winner == "Editorial Desire"
    assert session.selected_direction == "Editorial Desire"
    assert session.status == "direction_selected"


def test_director_creates_revision():
    director = CreativeDirector()
    session = director.start(context())

    revision = director.revise(
        session,
        critique="The concept feels too generic.",
        weak_areas=[
            "distinctiveness",
            "composition",
            "emotional point of view",
        ],
    )

    assert revision.iteration == 1
    assert len(revision.changes) == 3
    assert session.status == "revision"


def test_human_approval_is_part_of_session():
    director = CreativeDirector()
    session = director.start(context())

    session.approve(
        "The direction feels right. Proceed to generation."
    )

    assert session.human_approved is True
    assert session.status == "approved"
