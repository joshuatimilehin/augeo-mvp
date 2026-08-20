from creative.brand.guard import BrandGuard
from creative.brand.manager import BrandManager
from creative.brand.profile import ApprovedLogo, BrandProfile


class FakeDatabase:
    def __init__(self):
        self.rows = {}

    def get_brand_memory(self, phone):
        return self.rows.get(phone)

    def save_brand_memory(self, phone, **fields):
        row = dict(self.rows.get(phone) or {})
        row.update(fields)
        self.rows[phone] = row


def test_brand_manager_registers_and_preserves_approved_logo():
    db = FakeDatabase()
    manager = BrandManager(db)

    profile = manager.register_logo(
        "2348000000000",
        "assets/brands/test/logo.png",
        asset_id="logo-001",
    )

    assert profile.has_approved_logo
    assert profile.logo.path == "assets/brands/test/logo.png"
    assert profile.logo.asset_id == "logo-001"

    reloaded = manager.get_profile("2348000000000")
    assert reloaded.has_approved_logo
    assert reloaded.logo.path == "assets/brands/test/logo.png"


def test_brand_manager_recommends_logo_when_missing():
    db = FakeDatabase()
    manager = BrandManager(db)

    assert manager.logo_recommendation("2348000000000") is not None

    manager.save_profile(
        "2348000000000",
        BrandProfile(
            business_name="Augeo Test Brand",
            logo=ApprovedLogo("assets/brands/test/logo.png"),
        ),
    )

    assert manager.logo_recommendation("2348000000000") is None


def test_brand_guard_rejects_wrong_logo():
    profile = BrandProfile(
        business_name="Augeo Test Brand",
        logo=ApprovedLogo("assets/brands/test/logo.png"),
    )

    result = BrandGuard().validate_logo_reference(
        "assets/brands/other/logo.png",
        profile,
    )

    assert result.allowed is False
    assert result.issues


def test_brand_guard_rejects_prohibited_brand_language():
    profile = BrandProfile(
        business_name="Augeo Test Brand",
        avoid_words=["cheap", "guaranteed"],
    )

    result = BrandGuard().validate_text(
        "This is a cheap product with guaranteed results.",
        profile,
    )

    assert result.allowed is False
    assert len(result.issues) == 2
