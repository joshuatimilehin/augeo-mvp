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

    library.add(
        PromptRecord(
            id="retail-luxury-product",
            category="retail",
            subcategory="product",
            visual_style="luxury",
            language="english-market",
            name="Luxury Retail Product",
            source="internal",
            tags=[
                "retail",
                "product",
                "luxury",
                "fashion",
                "commercial",
                "social",
            ],
            template="""
Create a premium commercial retail product advertisement.

Hero product:
{product_description}

Target audience:
{audience}

Location:
{location}

Visual direction:
luxury editorial composition,
premium commercial advertising,
sophisticated lighting,
clean high-end presentation,
realistic materials and textures,
strong product focus,
elegant Nigerian social-commerce aesthetic.

Brand:
{brand_name}

Headline:
{headline}

Price:
{price}

The product must remain the unmistakable hero.
Create a polished, aspirational advertisement suitable
for WhatsApp Status and social media selling.
""".strip(),
        )
    )
    library.add(
        PromptRecord(
            id="generic-commercial-product",
            category="generic",
            subcategory="commercial",
            visual_style="luxury",
            language="english-market",
            name="Universal Commercial Product",
            source="internal",
            tags=[
                "generic",
                "commercial",
                "product",
                "social",
                "whatsapp",
            ],
            template="""
Create a polished commercial advertisement for a Nigerian business.

Hero offering:
{product_description}

Target audience:
{audience}

Location:
{location}

Visual direction:
professional commercial composition,
strong visual hierarchy,
premium presentation,
clean typography,
realistic materials,
clear product or service focus,
social-media-ready advertising aesthetic.

Brand:
{brand_name}

Headline:
{headline}

Price or offer:
{price}

Make the offering immediately understandable and desirable.
The final design should feel professionally produced and
appropriate for WhatsApp Status and social media commerce.
""".strip(),
        )
    )

    library.add(
        PromptRecord(
            id="generic-service",
            category="generic-service",
            subcategory="service",
            visual_style="minimal",
            language="english-market",
            name="Universal Service Advertisement",
            source="internal",
            tags=[
                "generic",
                "service",
                "business",
                "professional",
                "social",
            ],
            template="""
Create a professional advertisement for a Nigerian service business.

Service:
{product_description}

Target audience:
{audience}

Location:
{location}

Visual direction:
clean professional composition,
clear information hierarchy,
credible business presentation,
modern typography,
strong focal point,
trustworthy commercial aesthetic.

Brand:
{brand_name}

Headline:
{headline}

Price or offer:
{price}

Make the service immediately understandable and compelling.
The final design should be suitable for WhatsApp Status,
Instagram, and other social platforms.
""".strip(),
        )
    )
    
    return library