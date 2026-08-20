# skill-quotes

## What this skill governs
Standalone quote designs -- no user photo required. Typography carries the entire design. This is the cleanest category to get right because there's no competing visual element (no photo, no logo) fighting the text for attention.

## Core taste rules
1. **One line leads.** The quote itself is the dominant element on the canvas. Attribution (if present) is secondary and quiet -- never competes in size or weight.
2. **Two fonts, no more.** One for the quote, one for attribution/accent. This is a hard ceiling, not a guideline -- see config.json `max_fonts_per_design`.
3. **Whitespace is not empty space.** Minimum 10% margin on all sides (see `fallback_static_layout.margin_pct`). Resist the urge to fill the canvas.
4. **Short lines over long lines.** Break the quote across multiple short lines rather than letting it run edge to edge -- this is especially true for the editorial_literary pairing.
5. **Mobile legibility floor.** Headline text never drops below 24pt regardless of quote length. If a long quote would force smaller text, prefer shrinking margins before shrinking below the floor.

## Mood selection (this is the judgment call)
When the user's description doesn't explicitly state a tone, infer mood from the quote's subject matter:
- Love, faith, grief, reflection, "ancient wisdom" register -> `elegant_reflective`
- Sports, hustle, achievement, "get up and go" -> `bold_motivational`
- Everyday encouragement, gratitude, general positivity -> `warm_everyday` (also the safe default)
- Poetic or philosophical phrasing, longer sentences -> `editorial_literary`
- Casual, slang-adjacent, clearly aimed at a younger audience -> `youthful_social`

If genuinely ambiguous, default to `warm_everyday` -- it's the safest pairing and reads as intentional rather than generic.

## What NOT to do
- Do not introduce a third font under any circumstances, even if the user requests "something extra fancy."
- Do not center-justify long multi-line quotes if it creates a ragged, hard-to-scan block -- left-align if line count exceeds 3.
- Do not let attribution text approach headline size -- it should read as a footnote, not a co-headline.
