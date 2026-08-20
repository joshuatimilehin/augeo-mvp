from typing import Optional

from .profile import ApprovedLogo, BrandProfile


class BrandManager:
    """
    Thin brand-intelligence layer.

    Responsibilities:
      1. Load/save the customer's persistent brand profile.
      2. Treat uploaded logos as approved immutable assets.
      3. Provide compact brand context to the existing creative engine.
      4. Recommend logo creation only when no approved logo exists.

    It intentionally does NOT generate images, replace CustomerContext, or
    replace PromptRetriever. It sits above those systems.
    """

    def __init__(self, database_module):
        self.db = database_module

    def get_profile(self, customer_phone: str) -> BrandProfile:
        row = self.db.get_brand_memory(customer_phone)
        if not row:
            return BrandProfile()
        return self._profile_from_legacy_row(row)

    def save_profile(
        self,
        customer_phone: str,
        profile: BrandProfile,
    ) -> BrandProfile:
        logo_path = profile.logo.path if profile.logo else None

        self.db.save_brand_memory(
            customer_phone,
            business_name=profile.business_name,
            primary_color=profile.primary_color,
            secondary_color=profile.secondary_color,
            logo_path=logo_path,
            preferred_language=profile.preferred_language,
            preferred_tone=profile.preferred_tone,
            common_phrases=", ".join(profile.common_phrases),
            avoid_words=", ".join(profile.avoid_words),
            category_focus=profile.category_focus,
            template_preference=profile.template_preference,
        )

        return profile

    def register_logo(
        self,
        customer_phone: str,
        logo_path: str,
        asset_id: Optional[str] = None,
    ) -> BrandProfile:
        """
        Register the customer's supplied logo.

        Important: this stores the asset reference; it does not transform,
        redraw, stylize, or send the logo to an image generator.
        """
        profile = self.get_profile(customer_phone)
        profile.logo = ApprovedLogo(
            path=logo_path,
            asset_id=asset_id,
        )
        return self.save_profile(customer_phone, profile)

    def build_creative_context(self, customer_phone: str) -> dict:
        """
        Compact context that can be injected into prompt/layout generation.
        """
        profile = self.get_profile(customer_phone)

        return {
            "business_name": profile.business_name,
            "primary_color": profile.primary_color,
            "secondary_color": profile.secondary_color,
            "preferred_language": profile.preferred_language,
            "preferred_tone": profile.preferred_tone,
            "common_phrases": profile.common_phrases,
            "avoid_words": profile.avoid_words,
            "category_focus": profile.category_focus,
            "template_preference": profile.template_preference,
            "approved_logo": (
                {
                    "path": profile.logo.path,
                    "asset_id": profile.logo.asset_id,
                    "usage_note": profile.logo.usage_note,
                }
                if profile.logo
                else None
            ),
        }

    def logo_recommendation(self, customer_phone: str) -> Optional[str]:
        profile = self.get_profile(customer_phone)
        if profile.has_approved_logo:
            return None

        return (
            "This business does not have an approved logo saved yet. "
            "Augeo can offer an optional logo-creation workflow before "
            "building future branded creatives."
        )

    @staticmethod
    def _profile_from_legacy_row(row: dict) -> BrandProfile:
        common_phrases = [
            item.strip()
            for item in (row.get("common_phrases") or "").split(",")
            if item.strip()
        ]
        avoid_words = [
            item.strip()
            for item in (row.get("avoid_words") or "").split(",")
            if item.strip()
        ]

        logo_path = row.get("logo_path")
        logo = ApprovedLogo(path=logo_path) if logo_path else None

        return BrandProfile(
            business_name=row.get("business_name") or "",
            primary_color=row.get("primary_color"),
            secondary_color=row.get("secondary_color"),
            preferred_language=row.get("preferred_language"),
            preferred_tone=row.get("preferred_tone"),
            common_phrases=common_phrases,
            avoid_words=avoid_words,
            category_focus=row.get("category_focus"),
            template_preference=row.get("template_preference"),
            logo=logo,
        )
