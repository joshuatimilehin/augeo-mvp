from creative.business_intelligence import BusinessProfile, BusinessResolver


class FakeBusinessProvider:
    def search(self, query, location=None):
        return [
            BusinessProfile(
                name="Example Skincare",
                category="Skincare",
                location="Lagos, Nigeria",
                website="https://example.com",
            )
        ]


def test_business_resolver_returns_business_profile():
    resolver = BusinessResolver(
        providers=[FakeBusinessProvider()]
    )

    results = resolver.resolve(
        "Example Skincare",
        "Lagos, Nigeria",
    )

    assert len(results) == 1
    assert results[0].name == "Example Skincare"
    assert results[0].website == "https://example.com"