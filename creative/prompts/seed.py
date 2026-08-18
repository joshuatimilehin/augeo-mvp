from creative.prompts.library import (
    PromptLibrary,
    PromptRecord,
)


def create_seed_library() -> PromptLibrary:
    """
    Create Augeo's initial prompt library.

    These are controlled internal templates.
    External prompt scraping will be added separately.
    """

    library = PromptLibrary()

    library.add(
        PromptRecord(
            id="fashion-luxury-product",
            category="fashion",
            subcategory="luxury",
            visual_style="luxury",
            language="english-market",
            name="Luxury Product Campaign",
            source="internal",
            tags=[
                "fashion",
                "luxury",
                "product",
                "commercial",
            ],
            template="""
Create a premium commercial fashion advertisement.

Hero product:
{product_description}

Target audience:
{audience}

Location:
{location}

Visual direction:
Luxury editorial photography,
premium commercial composition,
sophisticated lighting,
high-end product presentation,
photorealistic materials,
aspirational visual language.

Brand:
{brand_name}

Headline:
{headline}

Price:
{price}

The final image should feel like a professionally
produced premium fashion campaign.
""".strip(),
        )
    )

    library.add(
        PromptRecord(
            id="church-event",
            category="church",
            subcategory="event",
            visual_style="bold",
            language="english-market",
            name="Church Event Announcement",
            source="internal",
            tags=[
                "church",
                "event",
                "announcement",
                "social",
            ],
            template="""
Create a polished church event promotional graphic.

Event:
{product_description}

Audience:
{audience}

Location:
{location}

Visual direction:
clear hierarchy,
welcoming atmosphere,
strong focal point,
professional event-poster composition,
readable typography,
appropriate spiritual visual language.

Church/organization:
{brand_name}

Headline:
{headline}

Date/time:
{price}

The design should communicate the event immediately
while remaining visually sophisticated and inviting.
""".strip(),
        )
    )

    library.add(
        PromptRecord(
            id="food-commercial",
            category="food",
            subcategory="commercial",
            visual_style="bold",
            language="english-market",
            name="Food Commercial",
            source="internal",
            tags=[
                "food",
                "restaurant",
                "commercial",
                "social",
            ],
            template="""
Create a highly appetizing commercial food advertisement.

Product:
{product_description}

Target audience:
{audience}

Location:
{location}

Visual direction:
professional food photography,
appetizing presentation,
controlled studio lighting,
rich realistic textures,
strong focal composition,
premium commercial advertising aesthetic.

Brand:
{brand_name}

Headline:
{headline}

Price:
{price}

The final image should make the product immediately
desirable while maintaining a polished commercial identity.
""".strip(),
        )
    )

    return library