from dataclasses import dataclass, field
@dataclass
class BusinessProfile:
    name: str
    description: str | None = None
    category: str | None = None
    location: str | None = None
    website: str | None = None
    phone: str | None = None
    address: str | None = None
    rating: float | None = None
    review_count: int | None = None
    social_profiles: dict[str, str] = field(default_factory=dict)
    source_urls: list[str] = field(default_factory=list)
    raw_data: dict = field(default_factory=dict)