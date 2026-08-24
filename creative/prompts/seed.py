from creative.prompts.library import PromptLibrary, PromptRecord


def create_seed_library() -> PromptLibrary:
    """
    Augeo's production seed prompt library.

    These prompts provide broad category coverage.
    Discovered prompts can be added later through the
    discovery/evolution pipeline.
    """

    library = PromptLibrary()

    prompts = [
        PromptRecord(
            id="fashion-luxury-product",
            category="fashion",
            subcategory="luxury",
            visual_style="luxury",
            language="english-market",
            name="Luxury Fashion Product",
            source="internal",
            tags=["fashion", "luxury", "product", "commercial"],
            template="""
Voice guidance: {voice_instructions}
Locale: {locale}
Channel: {channel}

Create a premium commercial fashion advertisement.

Hero product:
{product_description}

Target audience:
{audience}

Location:
{location}

Visual direction:
luxury editorial photography,
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

Make the product immediately desirable and visually premium.
""".strip(),
        ),

        PromptRecord(
            id="retail-commercial-product",
            category="retail",
            subcategory="commercial",
            visual_style="commercial",
            language="english-market",
            name="Retail Product Advertisement",
            source="internal",
            tags=["retail", "product", "commercial", "whatsapp"],
            template="""
Voice guidance: {voice_instructions}
Locale: {locale}
Channel: {channel}

Create a polished commercial advertisement for a retail business.

Product:
{product_description}

Target audience:
{audience}

Location:
{location}

Visual direction:
professional product photography,
strong visual hierarchy,
clean composition,
realistic materials,
attractive commercial lighting,
social-media-ready presentation.

Brand:
{brand_name}

Headline:
{headline}

Price:
{price}

Make the product immediately understandable, trustworthy,
and desirable for customers.
""".strip(),
        ),

        PromptRecord(
            id="estate-property",
            category="estate",
            subcategory="property",
            visual_style="luxury",
            language="english-market",
            name="Real Estate Property Advertisement",
            source="internal",
            tags=["estate", "real-estate", "property", "luxury"],
            template="""
Voice guidance: {voice_instructions}
Locale: {locale}
Channel: {channel}

Create a premium real estate advertisement.

Property:
{product_description}

Target audience:
{audience}

Location:
{location}

Visual direction:
luxury architectural photography,
premium real-estate marketing,
bright sophisticated lighting,
elegant composition,
high-end property presentation,
aspirational lifestyle aesthetic.

Brand:
{brand_name}

Headline:
{headline}

Price:
{price}

Make the property feel desirable, valuable,
trustworthy, and professionally marketed.
""".strip(),
        ),

        PromptRecord(
            id="food-commercial",
            category="food",
            subcategory="commercial",
            visual_style="commercial",
            language="english-market",
            name="Food Commercial",
            source="internal",
            tags=["food", "restaurant", "commercial", "social"],
            template="""
Voice guidance: {voice_instructions}
Locale: {locale}
Channel: {channel}

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
rich realistic textures,
controlled studio lighting,
strong focal composition,
premium commercial advertising aesthetic.

Brand:
{brand_name}

Headline:
{headline}

Price:
{price}

Make the food immediately desirable and suitable
for WhatsApp Status and social media marketing.
""".strip(),
        ),

        PromptRecord(
            id="church-event",
            category="church",
            subcategory="event",
            visual_style="bold",
            language="english-market",
            name="Church Event Announcement",
            source="internal",
            tags=["church", "event", "announcement", "social"],
            template="""
Voice guidance: {voice_instructions}
Locale: {locale}
Channel: {channel}

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

Church or organization:
{brand_name}

Headline:
{headline}

Date or offer:
{price}

Make the event immediately understandable,
welcoming, and visually compelling.
""".strip(),
        ),

        PromptRecord(
            id="service-business",
            category="service",
            subcategory="commercial",
            visual_style="professional",
            language="english-market",
            name="Service Business Advertisement",
            source="internal",
            tags=["service", "business", "commercial", "social"],
            template="""
Voice guidance: {voice_instructions}
Locale: {locale}
Channel: {channel}

Create a professional advertisement for a Nigerian service business.

Service:
{product_description}

Target audience:
{audience}

Location:
{location}

Visual direction:
professional commercial design,
clear hierarchy,
trustworthy presentation,
modern typography,
strong focal composition,
clean social-media advertising aesthetic.

Brand:
{brand_name}

Headline:
{headline}

Price or offer:
{price}

Make the service immediately understandable,
credible, and compelling to potential customers.
""".strip(),
        ),

        PromptRecord(
            id="generic-commercial-product",
            category="generic",
            subcategory="commercial",
            visual_style="commercial",
            language="english-market",
            name="Universal Commercial Product",
            source="internal",
            tags=["generic", "commercial", "product", "social", "whatsapp"],
            template="""
Voice guidance: {voice_instructions}
Locale: {locale}
Channel: {channel}

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
        ),
    ]

    for prompt in prompts:
        library.add(prompt)

    return library