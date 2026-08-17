from dataclasses import dataclass
from typing import Optional


@dataclass
class CustomerContext:
    """
    Structured representation of the customer's creative request.

    This is the bridge between Augeo's existing conversation/skills
    system and the new Creative Intelligence layer.
    """

    category: str
    subcategory: Optional[str]

    product_name: str
    product_description: str

    price: Optional[str]
    brand_name: Optional[str]

    audience: Optional[str]
    location: Optional[str]

    language: Optional[str]
    visual_style: Optional[str]

    intent: Optional[str]
    occasion: Optional[str]

    @classmethod
    def from_order(
        cls,
        details: dict,
        graphic_skill_name: str,
        prompt_skill_name: str,
        category_skill_name: str,
        product_description: str,
        price_text: str,
    ) -> "CustomerContext":
        """
        Convert Augeo's existing order data and skill selections
        into the standardized CustomerContext object.
        """

        return cls(
            category=category_skill_name.replace("skill-", ""),
            subcategory=details.get("niche"),

            product_name=(
                details.get("product_name")
                or details.get("product")
                or details.get("name")
                or ""
            ),

            product_description=product_description,

            price=price_text,
            brand_name=details.get("brand_name"),

            audience=details.get("audience"),
            location=details.get("location"),

            language=prompt_skill_name.replace("skill-", ""),
            visual_style=graphic_skill_name.replace("skill-", ""),

            intent=details.get("intent"),
            occasion=details.get("occasion"),
        )