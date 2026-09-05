import json

from creative.context import CustomerContext
from creative.job import CreativeOrchestrator, MultimodalContext, ReferenceSignal
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


def test_creative_job_unifies_context_and_routing():
    orchestrator = CreativeOrchestrator()
    context = MultimodalContext(
        text=["I want a premium football launch video"],
        images=["https://example.com/reference.jpg"],
        urls=["https://example.com/product"],
        intent="launch campaign",
    )
    context.add_voice_note("This should feel premium and fast.")
    context.add_url("https://example.com/brand")

    job = orchestrator.create_job(
        intent="launch campaign",
        subject="football club launch",
        audience="fans and partners",
        context=context,
        desired_effect="make the product feel premium and high-energy",
        medium="video",
        format="launch_video",
        constraints=["premium", "high-energy", "football"],
        references=[ReferenceSignal(kind="inspiration", source="https://example.com/ref", summary="premium football feel")],
    )

    assert job.medium == "video"
    assert job.model_decision.primary_model == "astra-gpt-6"
    assert job.model_decision.fallback_model == "claude-fable-5-1"
    assert job.context.intent == "launch campaign"
    assert job.references[0].kind == "inspiration"


def test_orchestrator_can_create_a_structured_critique():
    orchestrator = CreativeOrchestrator()
    job = orchestrator.create_job(
        intent="launch campaign",
        subject="handbag campaign",
        audience="premium shoppers",
        desired_effect="make it feel luxurious",
        medium="image",
        format="static_image",
    )

    critique = orchestrator.evaluate(
        job,
        summary="Good direction but it needs more premium contrast.",
        weak_areas=["visual hierarchy", "luxury tone"],
        recommended_changes=["increase contrast", "tighten product framing"],
        score=0.81,
    )

    assert critique.score == 0.81
    assert len(job.revisions) == 1
    assert job.status.value == "revision"


def test_creative_job_persistence_has_unified_fields():
    from database import create_creative_job, get_creative_job

    job_id = create_creative_job(
        customer_phone="+2348000000000",
        job_type="launch_video",
        brief="Create a premium football launch video",
        context_json='{"intent": "launch campaign"}',
        direction='"Premium football launch"',
        production_plan_json='{"shots": 3}',
        assets_json='["https://example.com/ref.png"]',
        constraints_json='["premium", "football"]',
        provider="astra-gpt-6",
        status="ready",
        intent="launch campaign",
        subject="football launch video",
        audience="fans and partners",
        desired_effect="premium and energetic",
        medium="video",
        format="launch_video",
        references_json='[{"kind": "inspiration"}]',
        approval_state="pending",
        notes_json='["brief captured"]',
        memory_json='{"person": "creator"}',
    )

    job = get_creative_job(job_id)
    assert job is not None
    assert job["intent"] == "launch campaign"
    assert job["medium"] == "video"
    assert job["approval_state"] == "pending"
    assert json.loads(job["constraints_json"])[0] == "premium"
