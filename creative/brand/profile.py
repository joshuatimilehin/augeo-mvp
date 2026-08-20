from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ApprovedLogo:
    """
    Immutable-in-use brand asset.

    Augeo stores the path/reference to the approved source asset and never
    asks the image generator to redraw or modify it during normal generation.
    """
    path: str
    asset_id: Optional[str] = None
    usage_note: str = "Use the approved logo asset as supplied."


@dataclass
class BrandProfile:
    """
    Lightweight persistent brand profile.

    This deliberately stays small so it can sit above the existing creative
    intelligence system without replacing CustomerContext or PromptLibrary.
    """
    business_name: str = ""
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    preferred_language: Optional[str] = None
    preferred_tone: Optional[str] = None
    common_phrases: List[str] = field(default_factory=list)
    avoid_words: List[str] = field(default_factory=list)
    category_focus: Optional[str] = None
    template_preference: Optional[str] = None
    logo: Optional[ApprovedLogo] = None

    @property
    def has_approved_logo(self) -> bool:
        return self.logo is not None and bool(self.logo.path)

    @property
    def needs_logo(self) -> bool:
        return not self.has_approved_logo

    def to_dict(self) -> dict:
        return {
            "business_name": self.business_name,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "preferred_language": self.preferred_language,
            "preferred_tone": self.preferred_tone,
            "common_phrases": list(self.common_phrases),
            "avoid_words": list(self.avoid_words),
            "category_focus": self.category_focus,
            "template_preference": self.template_preference,
            "logo": (
                {
                    "path": self.logo.path,
                    "asset_id": self.logo.asset_id,
                    "usage_note": self.logo.usage_note,
                }
                if self.logo
                else None
            ),
        }

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "BrandProfile":
        data = data or {}
        logo_data = data.get("logo")
        logo = None
        if isinstance(logo_data, dict) and logo_data.get("path"):
            logo = ApprovedLogo(
                path=logo_data["path"],
                asset_id=logo_data.get("asset_id"),
                usage_note=logo_data.get(
                    "usage_note",
                    "Use the approved logo asset as supplied.",
                ),
            )

        return cls(
            business_name=data.get("business_name", ""),
            primary_color=data.get("primary_color"),
            secondary_color=data.get("secondary_color"),
            preferred_language=data.get("preferred_language"),
            preferred_tone=data.get("preferred_tone"),
            common_phrases=list(data.get("common_phrases") or []),
            avoid_words=list(data.get("avoid_words") or []),
            category_focus=data.get("category_focus"),
            template_preference=data.get("template_preference"),
            logo=logo,
        )
