from dataclasses import dataclass


@dataclass(frozen=True)
class CreativeCategory:
    id: str
    name: str
    description: str
    aliases: tuple[str, ...] = ()


CREATIVE_CATEGORIES = (
    CreativeCategory(
        id="fashion",
        name="Fashion & Apparel",
        description="Clothing, shoes, bags, accessories, beauty and personal style products.",
        aliases=("clothing", "apparel", "shoes", "bags", "accessories", "beauty"),
    ),
    CreativeCategory(
        id="food",
        name="Food & Restaurants",
        description="Food products, restaurants, catering, meals and food promotions.",
        aliases=("restaurant", "food", "catering", "meals", "drinks"),
    ),
    CreativeCategory(
        id="church",
        name="Church & Ministry",
        description="Church services, programs, events and ministry announcements.",
        aliases=("ministry", "church", "fellowship", "religious"),
    ),
    CreativeCategory(
        id="retail",
        name="Retail & Products",
        description="General consumer products and retail promotions.",
        aliases=("shop", "store", "product", "retail"),
    ),
    CreativeCategory(
        id="real_estate",
        name="Real Estate",
        description="Property sales, rentals, estates, apartments and land promotions.",
        aliases=("estate", "real estate", "property", "apartment", "house", "land"),
    ),
    CreativeCategory(
        id="services",
        name="Professional Services",
        description="Businesses selling services rather than physical products.",
        aliases=("service", "services", "consulting", "agency"),
    ),
    CreativeCategory(
        id="events",
        name="Events & Entertainment",
        description="Parties, concerts, weddings, birthdays and entertainment events.",
        aliases=("event", "party", "concert", "wedding", "birthday"),
    ),
    CreativeCategory(
        id="education",
        name="Education",
        description="Schools, courses, tutoring, training and educational programs.",
        aliases=("school", "course", "training", "academy", "tutoring"),
    ),
    CreativeCategory(
        id="health",
        name="Health & Wellness",
        description="Clinics, wellness businesses, fitness and health-related services.",
        aliases=("clinic", "fitness", "gym", "wellness"),
    ),
)


def get_category(category_id: str) -> CreativeCategory | None:
    category_id = category_id.strip().lower()

    for category in CREATIVE_CATEGORIES:
        if category.id == category_id:
            return category

    return None


def resolve_category(value: str) -> str | None:
    """
    Resolve a user/business category or alias to a canonical category ID.
    """

    value = value.strip().lower()

    for category in CREATIVE_CATEGORIES:
        if value == category.id:
            return category.id

        if value == category.name.lower():
            return category.id

        if value in category.aliases:
            return category.id

    return None


def all_category_ids() -> list[str]:
    return [category.id for category in CREATIVE_CATEGORIES]