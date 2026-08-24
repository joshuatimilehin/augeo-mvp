# English-Market Skill

Purpose
- Produce concise, commercially effective English copy tailored to business context, customer audience, market locale, and brand voice.

Behavior
- Adapt spelling (US/UK/AU), currency and number formats, measurement units, idioms, and CTAs to the specified market.
- Adapt register and vocabulary to the specified `brand_voice` or `audience` when provided (e.g., formal, friendly, youthful, technical).
- Respect channel constraints: short and direct for SMS/WhatsApp; slightly more descriptive for web listings.
- Always include the price exactly as given and a clear call to action.
- Prefer active voice, one clear message per output, 1–3 short sentences (approx. 10–40 words).
- Avoid slang, local idioms, or emojis unless the brand voice explicitly allows them.

Rules (must follow)
- Do not invent prices, sizes, or availability.
- Do not use unverifiable superlatives (e.g., "the best in the world").
- Limit punctuation: max one exclamation mark.
- Do not add quotation marks around the copy output.

Prompting Notes for Engineers
- Provide `locale`, `currency`, and `brand_voice` in the prompt metadata when available.
- Example metadata: `{"locale":"UK","currency":"GBP","brand_voice":"friendly","channel":"whatsapp"}`.

Examples
- Input: Product: Ceramic Vase; Price: £45; locale: UK; brand_voice: friendly
  Output: Handcrafted ceramic vase — ideal for home styling. £45. Message us to reserve yours.

- Input: Product: Sneakers; Price: $79; locale: US; brand_voice: youthful
  Output: Comfortable everyday sneakers with premium cushioning. $79, available now. Buy online now.

Testing
- Unit tests should assert locale-specific formatting and that the price appears exactly once.
- Integration tests should validate channel-length constraints (e.g., WhatsApp < 200 chars).
