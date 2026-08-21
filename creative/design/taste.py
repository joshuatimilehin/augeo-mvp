from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ColorRelationship:
    name: str
    colors: List[str]
    qualities: List[str]
    suitable_for: List[str]


@dataclass(frozen=True)
class TypographyRelationship:
    name: str
    fonts: List[str]
    qualities: List[str]
    suitable_for: List[str]


@dataclass(frozen=True)
class CompositionPattern:
    name: str
    principles: List[str]
    suitable_for: List[str]


COLOR_RELATIONSHIPS = [
    ColorRelationship(
        name="green-cream",
        colors=["green", "cream"],
        qualities=["natural", "premium", "calm", "refined"],
        suitable_for=[
            "luxury",
            "wellness",
            "organic",
            "fashion",
            "lifestyle",
        ],
    ),
    ColorRelationship(
        name="black-gold",
        colors=["black", "gold"],
        qualities=["luxury", "prestige", "premium", "dramatic"],
        suitable_for=[
            "luxury",
            "fashion",
            "jewelry",
            "hospitality",
        ],
    ),
    ColorRelationship(
        name="navy-cream",
        colors=["navy", "cream"],
        qualities=["trustworthy", "professional", "timeless", "refined"],
        suitable_for=[
            "finance",
            "professional-services",
            "luxury",
            "corporate",
        ],
    ),
]


TYPOGRAPHY_RELATIONSHIPS = [
    TypographyRelationship(
        name="serif-sans",
        fonts=["serif", "sans-serif"],
        qualities=["editorial", "premium", "balanced", "modern"],
        suitable_for=[
            "fashion",
            "luxury",
            "editorial",
            "hospitality",
        ],
    ),
    TypographyRelationship(
        name="bold-sans",
        fonts=["bold sans-serif"],
        qualities=["confident", "modern", "clear", "energetic"],
        suitable_for=[
            "sports",
            "technology",
            "events",
            "youth",
        ],
    ),
    TypographyRelationship(
        name="minimal-sans",
        fonts=["clean sans-serif"],
        qualities=["minimal", "clean", "modern", "accessible"],
        suitable_for=[
            "technology",
            "startups",
            "professional-services",
            "lifestyle",
        ],
    ),
]


COMPOSITION_PATTERNS = [
    CompositionPattern(
        name="hero-product",
        principles=[
            "single dominant product",
            "strong visual hierarchy",
            "negative space",
            "clear headline",
        ],
        suitable_for=[
            "product-advertisement",
            "fashion",
            "luxury",
            "ecommerce",
        ],
    ),
    CompositionPattern(
        name="editorial",
        principles=[
            "strong imagery",
            "asymmetric balance",
            "restrained typography",
            "intentional negative space",
        ],
        suitable_for=[
            "fashion",
            "luxury",
            "culture",
            "lifestyle",
        ],
    ),
]


def get_color_relationships(category: str) -> list[ColorRelationship]:
    category = category.lower()

    return [
        relationship
        for relationship in COLOR_RELATIONSHIPS
        if category in relationship.suitable_for
    ]


def get_typography_relationships(category: str) -> list[TypographyRelationship]:
    category = category.lower()

    return [
        relationship
        for relationship in TYPOGRAPHY_RELATIONSHIPS
        if category in relationship.suitable_for
    ]


def get_composition_patterns(category: str) -> list[CompositionPattern]:
    category = category.lower()

    return [
        pattern
        for pattern in COMPOSITION_PATTERNS
        if category in pattern.suitable_for
    ]