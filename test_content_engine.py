from creative.content import ContentPlanner
from creative.content_orchestrator import ContentOrchestrator


def test_content_planner_creates_complete_smb_content_pack():
    plan = ContentPlanner().plan(
        product="Luxury Black Leather Handbag",
        audience="young professionals",
        objective="increase product interest",
    )

    kinds = {piece.kind for piece in plan.pieces}

    assert "hero_image" in kinds
    assert "lifestyle_image" in kinds
    assert "ugc_video" in kinds
    assert "social_caption" in kinds
    assert "alternative_ad" in kinds


def test_content_planner_selects_expected_providers():
    plan = ContentPlanner().plan(
        product="Luxury Black Leather Handbag",
        audience="young professionals",
        objective="increase product interest",
    )

    providers = {piece.kind: piece.provider for piece in plan.pieces}

    assert providers["hero_image"] == "ideogram"
    assert providers["lifestyle_image"] == "ideogram"
    assert providers["ugc_video"] == "seedance"
    assert providers["social_caption"] == "openai"


def test_content_orchestrator_does_not_fake_generation():
    orchestrator = ContentOrchestrator()

    plan = orchestrator.create_plan(
        product="Luxury Black Leather Handbag",
    )

    result = orchestrator.execute_plan(plan)

    assert result["status"] == "planned"
    assert len(result["jobs"]) == 5
    assert all(job["status"] == "planned" for job in result["jobs"])
