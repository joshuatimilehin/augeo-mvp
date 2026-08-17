"""
Augeo Generative Layout Engine
-------------------------------
Given a product, a chosen graphic skill, and (optionally) brand memory
and prior layouts, ask GPT-4o-mini to design a unique flyer layout as
JSON, constrained by the skill's SKILL.md taste rules and config.json.

The model never touches pixels directly. It returns a spec; Pillow draws
it (see flyer_generator.FlyerGenerator.create_flyer_from_layout).

Every call is wrapped so a bad/missing API key, a network failure, or a
malformed response falls back to a deterministic layout derived from the
skill's static config.json — the flyer generator never breaks, it just
loses variety for that one flyer.
"""

import json
import re
from typing import Any, Dict, List, Optional

from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = "gpt-4o-mini"

# Fields the model is allowed to control, and their safe bounds. Used both
# in the prompt and to clamp whatever comes back.
CANVAS_SIZE = 1080


def _load_skill_taste(skill: Dict[str, Any]) -> str:
    """Pull the SKILL.md taste rules + a trimmed config.json as text context."""
    skill_dir = skill.get('skill_dir')
    parts: List[str] = []

    if skill_dir:
        skill_md = skill_dir / 'SKILL.md'
        if skill_md.exists():
            parts.append(skill_md.read_text(encoding='utf-8'))

    config = skill.get('config', {})
    design_fields = {
        k: v for k, v in config.items()
        if k in (
            'name', 'description', 'background_color', 'background_gradient',
            'price_color', 'text_color', 'accent_color', 'forbidden',
            'required', 'layout_rules',
        )
    }
    if design_fields:
        parts.append("Technical defaults (use as a starting palette, not a rigid grid):\n"
                      + json.dumps(design_fields, indent=2))

    return "\n\n".join(parts)


def _font_pairings_context(skill: Dict[str, Any]) -> str:
    """If this skill defines a font-pairing library (skill-quotes and similar
    typography-led skills), list the available moods so the model can choose
    one deliberately instead of guessing at font names. Skills without
    font_pairings (product flyers, etc.) get an empty string here and are
    completely unaffected — this is additive, not a schema change for them."""
    pairings = skill.get('config', {}).get('font_pairings')
    if not isinstance(pairings, list) or not pairings:
        return ""

    moods = []
    for p in pairings:
        mood = p.get('mood')
        desc = p.get('description', '')
        if mood:
            moods.append(f"- {mood}: {desc}")

    if not moods:
        return ""

    return (
        "## Typography mood (this skill is typography-led)\n"
        "Choose exactly one mood from this list based on the content's tone. "
        "Do not invent a mood name not listed here:\n"
        + "\n".join(moods)
    )


def _brand_context(brand_memory: Optional[Dict[str, Any]]) -> str:
    if not brand_memory:
        return ""
    return (
        "Brand memory for this returning customer — reuse their colors if set:\n"
        f"- Primary color: {brand_memory.get('primary_color') or 'not set'}\n"
        f"- Secondary color: {brand_memory.get('secondary_color') or 'not set'}\n"
        f"- Preferred tone: {brand_memory.get('preferred_tone') or 'not set'}\n"
    )


def _previous_layouts_context(previous_layouts: Optional[List[Dict[str, Any]]]) -> str:
    if not previous_layouts:
        return ""
    recent = previous_layouts[-3:]
    return (
        "This customer's last few layouts (avoid repeating the same photo "
        "position / accent arrangement — vary it):\n"
        + json.dumps(recent, indent=2)
    )


SYSTEM_PROMPT_TEMPLATE = """You are Augeo's flyer layout designer. You design \
one 1080x1080 Instagram-style product flyer layout at a time for Nigerian \
small-business sellers, expressed as strict JSON that a Python/Pillow \
renderer will draw exactly as specified.

## Skill context (your taste constraints for this flyer)
{skill_context}

{brand_context}

{previous_context}

{typography_context}

## Output — return ONLY this JSON shape, nothing else, no markdown fences
{{
  "background": {{"type": "gradient|solid", "colors": ["#hex", "#hex"], "direction": "vertical|horizontal|diagonal"}},
  "photo": {{"x": int, "y": int, "width": int, "height": int, "border_radius": int, "shadow": true|false}},
  "price": {{"x": int, "y": int, "size": int, "color": "#hex", "bg_shape": "none|pill|rectangle", "bg_color": "#hex"}},
  "caption": {{"x": int, "y": int, "size": int, "color": "#hex", "max_width": int, "line_height": int, "align": "left|center", "bg_shape": "none|rounded_rect", "bg_color": "#hex"}},
  "accents": [{{"type": "line|circle|rectangle", "coords": [x1, y1, x2, y2], "color": "#hex", "width": int}}],
  "brand_mark": {{"text": "AUGEO", "x": int, "y": int, "size": int, "color": "#hex"}},
  "typography": {{"mood": "mood_key_from_list_above_or_omit_if_none_listed"}}
}}

## Hard rules
1. All coordinates must fit inside a 1080x1080 canvas with at least 20px margin.
2. photo.x + photo.width <= 1040, photo.y + photo.height <= 1040. Keep the photo roughly centered horizontally (x between 100 and 650).
3. Price must be legible: strong contrast against its background.
4. Caption sits below or beside the photo, never overlapping it.
5. 2 to 4 accents maximum. Follow the skill's forbidden/required lists exactly.
6. Never invent colors outside the skill's palette family (e.g. don't put red in a luxury layout).
7. Design from these constraints only — do not reference or approximate any specific real advertisement, brand's layout, or existing flyer you may recall. Compose an original arrangement within the skill's rules.
8. Return ONLY the JSON object. No prose, no markdown code fences, no comments.
"""


def generate_layout(
    product_description: str,
    price: str,
    graphic_skill: Dict[str, Any],
    brand_memory: Optional[Dict[str, Any]] = None,
    previous_layouts: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Return a validated layout dict. Never raises — falls back on any failure."""
    try:
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            skill_context=_load_skill_taste(graphic_skill),
            brand_context=_brand_context(brand_memory),
            previous_context=_previous_layouts_context(previous_layouts),
            typography_context=_font_pairings_context(graphic_skill),
        )
        user_prompt = f"Product: {product_description}\nPrice: {price}\n\nDesign a unique flyer layout."

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=900,
            temperature=0.9,
            timeout=15,
        )
        raw = response.choices[0].message.content
        layout = json.loads(raw)
        return _validate_and_clamp(layout, graphic_skill)
    except Exception as e:
        print(f"[layout_engine] generation failed, using fallback: {e}")
        return _fallback_layout(graphic_skill)


_HEX_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')


def _safe_hex(value: Any, default: str) -> str:
    if isinstance(value, str) and _HEX_RE.match(value):
        return value
    return default


def _clamp(value: Any, lo: int, hi: int, default: int) -> int:
    try:
        v = int(value)
    except (TypeError, ValueError):
        return default
    return max(lo, min(v, hi))


def _resolve_typography(requested_mood: Any, graphic_skill: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Turn the model's chosen mood (a string) into the concrete font info
    flyer_generator.py needs to actually load the font — file names,
    per-element point sizes, and, for variable-weight fonts, which named
    instance to select via set_variation_by_name(). Never trusts the model's
    mood string blindly: falls back to the skill's default_mood, then to the
    first defined pairing, then to None if the skill has no font_pairings at
    all (product-flyer skills are unaffected and get no typography key)."""
    config = graphic_skill.get('config', {})
    pairings = config.get('font_pairings')
    if not isinstance(pairings, list) or not pairings:
        return None

    by_mood = {p.get('mood'): p for p in pairings if isinstance(p, dict) and p.get('mood')}
    default_mood = config.get('default_mood')

    chosen = None
    if isinstance(requested_mood, str) and requested_mood in by_mood:
        chosen = by_mood[requested_mood]
    elif default_mood in by_mood:
        chosen = by_mood[default_mood]
    elif pairings:
        chosen = pairings[0]

    if not chosen:
        return None

    fonts_dir = config.get('fonts_directory', 'fonts')

    return {
        "mood": chosen.get("mood"),
        "headline_font": f"{fonts_dir}/{chosen.get('headline_font')}" if chosen.get('headline_font') else None,
        "headline_variation": chosen.get("headline_variation"),
        "headline_pt": chosen.get("headline_pt"),
        "accent_font": f"{fonts_dir}/{chosen.get('accent_font')}" if chosen.get('accent_font') else None,
        "accent_variation": chosen.get("accent_variation"),
        "accent_pt": chosen.get("accent_pt"),
    }


def _validate_and_clamp(layout: Dict[str, Any], graphic_skill: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Defensive validation — never trust the model's numbers blindly."""
    out: Dict[str, Any] = {}

    bg = layout.get("background") or {}
    colors = bg.get("colors")
    if not isinstance(colors, list) or not colors:
        colors = ["#1a1a2e", "#0a0a12"]
    colors = [_safe_hex(c, "#1a1a2e") for c in colors][:3] or ["#1a1a2e"]
    out["background"] = {
        "type": bg.get("type") if bg.get("type") in ("gradient", "solid") else "gradient",
        "colors": colors,
        "direction": bg.get("direction") if bg.get("direction") in ("vertical", "horizontal", "diagonal") else "vertical",
    }

    photo = layout.get("photo") or {}
    p_width = _clamp(photo.get("width"), 300, 700, 500)
    p_height = _clamp(photo.get("height"), 300, 700, 500)
    p_x = _clamp(photo.get("x"), 20, CANVAS_SIZE - p_width - 20, int((CANVAS_SIZE - p_width) / 2))
    p_y = _clamp(photo.get("y"), 20, CANVAS_SIZE - p_height - 260, 140)
    out["photo"] = {
        "x": p_x, "y": p_y, "width": p_width, "height": p_height,
        "border_radius": _clamp(photo.get("border_radius"), 0, 60, 20),
        "shadow": bool(photo.get("shadow", True)),
    }

    price = layout.get("price") or {}
    out["price"] = {
        "x": _clamp(price.get("x"), 20, CANVAS_SIZE - 40, 80),
        "y": _clamp(price.get("y"), 20, CANVAS_SIZE - 40, 80),
        "size": _clamp(price.get("size"), 24, 60, 44),
        "color": _safe_hex(price.get("color"), "#FFD700"),
        "bg_shape": price.get("bg_shape") if price.get("bg_shape") in ("none", "pill", "rectangle") else "none",
        "bg_color": _safe_hex(price.get("bg_color"), "#00000080") if isinstance(price.get("bg_color"), str) and len(price.get("bg_color", "")) == 6 else "#000000",
    }

    caption = layout.get("caption") or {}
    out["caption"] = {
        "x": _clamp(caption.get("x"), 20, CANVAS_SIZE - 40, 80),
        "y": _clamp(caption.get("y"), 20, CANVAS_SIZE - 40, 700),
        "size": _clamp(caption.get("size"), 18, 40, 28),
        "color": _safe_hex(caption.get("color"), "#FFFFFF"),
        "max_width": _clamp(caption.get("max_width"), 400, 1000, 920),
        "line_height": _clamp(caption.get("line_height"), 24, 56, 38),
        "align": caption.get("align") if caption.get("align") in ("left", "center") else "left",
        "bg_shape": caption.get("bg_shape") if caption.get("bg_shape") in ("none", "rounded_rect") else "none",
        "bg_color": caption.get("bg_color") if isinstance(caption.get("bg_color"), str) else None,
    }

    accents_in = layout.get("accents")
    accents_out = []
    if isinstance(accents_in, list):
        for a in accents_in[:4]:
            if not isinstance(a, dict):
                continue
            a_type = a.get("type")
            coords = a.get("coords")
            if a_type not in ("line", "circle", "rectangle") or not isinstance(coords, list):
                continue
            safe_coords = []
            for c in coords[:4]:
                safe_coords.append(_clamp(c, 0, CANVAS_SIZE, 0))
            accents_out.append({
                "type": a_type,
                "coords": safe_coords,
                "color": _safe_hex(a.get("color"), "#D4AF37"),
                "width": _clamp(a.get("width"), 1, 8, 2),
            })
    out["accents"] = accents_out

    brand_mark = layout.get("brand_mark") or {}
    out["brand_mark"] = {
        "text": str(brand_mark.get("text", "AUGEO"))[:20],
        "x": _clamp(brand_mark.get("x"), 0, CANVAS_SIZE - 100, CANVAS_SIZE - 110),
        "y": _clamp(brand_mark.get("y"), 0, CANVAS_SIZE - 20, CANVAS_SIZE - 30),
        "size": _clamp(brand_mark.get("size"), 8, 20, 14),
        "color": brand_mark.get("color") if isinstance(brand_mark.get("color"), str) else "#FFFFFF64",
    }

    if graphic_skill is not None:
        typography = _resolve_typography(
            (layout.get("typography") or {}).get("mood"), graphic_skill
        )
        if typography is not None:
            out["typography"] = typography

    return out


def _resolve_position(value, width: int, height: int, element_width: int = 0, element_height: int = 0, default=(80, 700)):
    """Mirror FlyerGenerator._normalize_position so the fallback layout
    actually reflects each skill's configured position, not a generic one."""
    if isinstance(value, str):
        positions = {
            'top-right': (width - element_width - 40, 60),
            'top-left': (40, 60),
            'bottom-left': (40, height - 120),
            'bottom-right': (width - element_width - 40, height - 120),
            'center': (int((width - element_width) / 2), int((height - element_width) / 2)),
        }
        return positions.get(value, default)
    if isinstance(value, (list, tuple)) and len(value) == 2:
        try:
            return (int(value[0]), int(value[1]))
        except (ValueError, TypeError):
            pass
    return default


def _fallback_layout(graphic_skill: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic layout built straight from the skill's static config.json.
    Used whenever the LLM call fails — same visual family, zero variety, zero risk."""
    config = graphic_skill.get('config', {})
    photo_w = config.get('photo_width', 500)
    photo_h = config.get('photo_height', 500)
    photo_x = config.get('photo_x', int((CANVAS_SIZE - photo_w) / 2))
    photo_y = config.get('photo_y', 140)
    gradient = config.get('background_gradient') or [config.get('background_color', '#1a1a2e')]

    price_pos = _resolve_position(
        config.get('price_position', (80, 80)), CANVAS_SIZE, CANVAS_SIZE, default=(80, 80)
    )
    caption_pos = _resolve_position(
        config.get('caption_position', (80, 700)), CANVAS_SIZE, CANVAS_SIZE,
        element_width=photo_w, default=(80, 700)
    )

    fallback: Dict[str, Any] = {
        "background": {"type": "gradient" if len(gradient) > 1 else "solid", "colors": gradient, "direction": "vertical"},
        "photo": {
            "x": photo_x, "y": photo_y, "width": photo_w, "height": photo_h,
            "border_radius": 30 if config.get('rounded_photo') else 0,
            "shadow": bool(config.get('photo_shadow', True)),
        },
        "price": {
            "x": price_pos[0], "y": price_pos[1], "size": config.get('price_size', 44),
            "color": config.get('price_color', '#FFD700'),
            "bg_shape": "none", "bg_color": "#000000",
        },
        "caption": {
            "x": caption_pos[0], "y": caption_pos[1], "size": config.get('caption_size', 28),
            "color": config.get('text_color', '#FFFFFF'),
            "max_width": config.get('caption_width', 920),
            "line_height": config.get('caption_line_height', 38),
            "align": "left",
            "bg_shape": "rounded_rect" if config.get('text_bg') else "none",
            "bg_color": _rgba_list_to_hex(config.get('text_bg_color')) if config.get('text_bg') else None,
        },
        "accents": [],
        "brand_mark": {
            "text": config.get('brand_mark', 'AUGEO'), "x": CANVAS_SIZE - 110,
            "y": CANVAS_SIZE - 30, "size": 14, "color": "#FFFFFF64",
        },
    }

    # Fallback has no model output to read a mood from, so resolve straight
    # to the skill's default_mood. Skills without font_pairings get nothing
    # here, same as the LLM path.
    typography = _resolve_typography(None, graphic_skill)
    if typography is not None:
        fallback["typography"] = typography

    return fallback


def _rgba_list_to_hex(value) -> Optional[str]:
    """text_bg_color in config.json is an [r,g,b,a] list; the layout-based
    renderer expects a hex string. Convert, dropping alpha (renderer draws
    it as a solid fill)."""
    if not isinstance(value, list) or len(value) < 3:
        return None
    try:
        return '#%02X%02X%02X' % (int(value[0]), int(value[1]), int(value[2]))
    except (ValueError, TypeError):
        return None
