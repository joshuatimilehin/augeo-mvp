from creative.media_department import MediaDepartmentOrchestrator


def test_media_department_decides_content_from_business_context():
    department = MediaDepartmentOrchestrator()

    result = department.plan(
        business={
            "id": "lagos-skincare",
            "category": "skincare",
            "audience": "young women",
            "positioning": "premium",
        },
        objective="launch vitamin C serum",
        available_assets=["product_photo"],
        channels=["whatsapp", "instagram"],
    )

    assert result["status"] == "ready"
    assert result["decision_count"] >= 3

    formats = [item.format for item in result["decisions"]]

    assert "product_conversion_flyer" in formats
    assert "ugc_video" in formats
    assert "multi_asset_campaign" in formats


def test_media_department_remembers_real_business_outcomes():
    department = MediaDepartmentOrchestrator()

    department.record_outcome(
        business_id="lagos-skincare",
        campaign_id="launch-1",
        creative_id="ugc-001",
        channel="instagram",
        audience="young women",
        objective="product launch",
        cta="buy now",
        approved=True,
        revision_count=1,
        published=True,
        engagement=92,
        leads=14,
        sales=5,
        format="ugc_video",
    )

    learning = department.learn("lagos-skincare")

    assert learning["sample_size"] == 1
    assert "instagram" in learning["best_channels"]
    assert "ugc_video" in learning["best_formats"]


def test_media_department_does_not_require_sales_to_remember_learning():
    department = MediaDepartmentOrchestrator()

    department.record_outcome(
        business_id="restaurant-1",
        campaign_id="promo-1",
        creative_id="poster-001",
        channel="whatsapp",
        audience="local customers",
        objective="weekend promotion",
        approved=True,
        revision_count=2,
        published=True,
        engagement=40,
        format="product_conversion_flyer",
    )

    learning = department.learn("restaurant-1")

    assert learning["sample_size"] == 1
    assert learning["average_revisions"] == 2.0
