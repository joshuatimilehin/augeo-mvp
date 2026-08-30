from .models import BusinessProfile


class BusinessResolver:
    def __init__(self, providers=None):
        self.providers = providers or []

    def resolve(
        self,
        query: str,
        location: str | None = None,
    ) -> list[BusinessProfile]:
        results = []

        for provider in self.providers:
            results.extend(provider.search(query, location))

        return self._deduplicate(results)

    @staticmethod
    def _deduplicate(
        businesses: list[BusinessProfile],
    ) -> list[BusinessProfile]:
        seen = set()
        unique = []

        for business in businesses:
            key = (
                business.name.lower().strip(),
                (business.location or "").lower().strip(),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(business)

        return unique