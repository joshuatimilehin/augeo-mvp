from dataclasses import dataclass, field
from typing import List, Optional

from .profile import BrandProfile


@dataclass
class BrandGuardResult:
    allowed: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BrandGuard:
    """
    Deterministic V1 brand/IP guard.

    This is not legal trademark clearance. It is a product-level consistency
    guard that catches obvious brand violations before/after generation.
    """

    def validate_text(
        self,
        text: str,
        profile: BrandProfile,
    ) -> BrandGuardResult:
        text = text or ""
        lowered = text.casefold()

        issues = []
        warnings = []

        for word in profile.avoid_words:
            if word and word.casefold() in lowered:
                issues.append(f"Contains prohibited brand term: {word}")

        if profile.common_phrases:
            # We do not require every phrase; this is guidance, not a hard rule.
            warnings.append("Brand-approved phrases are available for copy generation.")

        return BrandGuardResult(
            allowed=not issues,
            issues=issues,
            warnings=warnings,
        )

    def validate_logo_reference(
        self,
        logo_path_used: Optional[str],
        profile: BrandProfile,
    ) -> BrandGuardResult:
        if not profile.has_approved_logo:
            return BrandGuardResult(
                allowed=True,
                warnings=["No approved logo exists; logo creation may be offered."],
            )

        if logo_path_used != profile.logo.path:
            return BrandGuardResult(
                allowed=False,
                issues=[
                    "Creative attempted to use a logo other than the customer's "
                    "approved logo asset."
                ],
            )

        return BrandGuardResult(allowed=True)

    def validate_creative(
        self,
        text: str,
        profile: BrandProfile,
        logo_path_used: Optional[str] = None,
    ) -> BrandGuardResult:
        text_result = self.validate_text(text, profile)
        logo_result = self.validate_logo_reference(logo_path_used, profile)

        return BrandGuardResult(
            allowed=text_result.allowed and logo_result.allowed,
            issues=text_result.issues + logo_result.issues,
            warnings=text_result.warnings + logo_result.warnings,
        )
