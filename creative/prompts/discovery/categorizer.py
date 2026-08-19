from dataclasses import dataclass


@dataclass
class CategorizedContent:
    category: str
    confidence: float
    text: str


class PromptCategorizer:
    """
    Assigns discovered content to a broad creative category.

    The categorizer is intentionally deterministic for now.
    A future AI-based categorizer can replace this class
    without changing the rest of the discovery pipeline.
    """

    CATEGORY_KEYWORDS = {
        "fashion": {
            "fashion",
            "clothing",
            "apparel",
            "handbag",
            "shoes",
            "jewelry",
            "boutique",
            "luxury",
            "beauty",
            "cosmetics",
        },
        "food": {
            "food",
            "restaurant",
            "cafe",
            "menu",
            "meal",
            "pizza",
            "burger",
            "cake",
            "catering",
            "bakery",
        },
        "church": {
            "church",
            "gospel",
            "worship",
            "ministry",
            "sermon",
            "prayer",
            "christian",
            "conference",
        },
        "estate": {
            "estate",
            "real estate",
            "property",
            "apartment",
            "house",
            "home",
            "land",
            "villa",
            "bedroom",
            "property development",
        },
        "automotive": {
            "car",
            "cars",
            "automotive",
            "vehicle",
            "motor",
            "auto",
            "dealership",
            "suv",
        },
        "education": {
            "school",
            "education",
            "course",
            "training",
            "academy",
            "university",
            "lesson",
            "learning",
        },
        "health": {
            "hospital",
            "clinic",
            "health",
            "medical",
            "doctor",
            "pharmacy",
            "wellness",
            "dental",
        },
        "technology": {
            "technology",
            "software",
            "app",
            "startup",
            "saas",
            "developer",
            "computer",
            "digital",
        },
        "events": {
            "event",
            "conference",
            "concert",
            "festival",
            "summit",
            "workshop",
            "celebration",
            "party",
        },
        "travel": {
            "travel",
            "hotel",
            "tourism",
            "vacation",
            "resort",
            "flight",
            "destination",
            "tour",
        },
        "professional-services": {
            "consulting",
            "consultant",
            "lawyer",
            "accounting",
            "agency",
            "marketing",
            "legal",
            "professional services",
        },
    }

    def categorize(
        self,
        text: str,
    ) -> CategorizedContent:

        normalized = text.lower()

        scores = {}

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0

            for keyword in keywords:
                if keyword in normalized:
                    score += 1

            scores[category] = score

        best_category = max(
            scores,
            key=scores.get,
        )

        best_score = scores[best_category]

        if best_score == 0:
            category = "generic"
            confidence = 0.0
        else:
            total_matches = sum(scores.values())

            confidence = min(
                1.0,
                best_score / max(total_matches, 1),
            )

            category = best_category

        return CategorizedContent(
            category=category,
            confidence=confidence,
            text=text,
        )