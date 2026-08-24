# Augeo — Update Notes

This package replaces your existing project folder. Everything here has
been read, fixed, and run through Flask's own test client — not just
pasted in blind.

## 1. Security — do this before anything else

Your OpenAI key was pasted into a chat with a third-party service (Kimi)
and has been circulating in plaintext across several files. Treat it as
burned:

1. Go to platform.openai.com → API keys → revoke the old one.
2. Generate a new key.
3. Put it in a fresh `.env` (copy `.env.example` → `.env` and fill it in).
   `.env` is **not** included in this package on purpose — don't commit
   it to git, and don't paste it into a chat again. On Render/Railway,
   set it as an environment variable in their dashboard instead.

## 2. What was actually broken

`main.py`'s Paystack webhook had a dead branch calling
`get_order_by_reference()` — a function that doesn't exist anywhere in
the codebase. It was leftover from an earlier single-order design that
got replaced by the credit-pack system. It wouldn't fire under normal
credit-pack purchases, but any webhook payload missing the expected
metadata would have thrown a `NameError` and 500'd. Removed.

The retention-check background timer was a non-daemon thread, which
means running `python main.py` locally (or any test harness) would hang
forever after the server otherwise finished, because the process never
exits while a non-daemon thread is alive. Harmless under gunicorn in
production, annoying everywhere else. Now a daemon thread.

## 3. What was missing and has been rebuilt

**`skills/` — the whole directory.** It was never in your uploads (you
have it locally, but it wasn't part of what you sent). Rebuilt from the
exact specs in your Kimi transcript:
- 5 graphic skills (luxury, bold, urgency, festive, minimal) — each with
  `config.json` matching your original numbers exactly, plus a new
  `SKILL.md` with the actual taste rules (forbidden/required elements,
  tone) that the layout engine now reads as design constraints.
- 1 language skill (English-market) — with
  `config.json`, `vocabulary.json`, `constraints.json`, `examples.json`.
- 4 category skills (fashion, beauty, food, retail) — lightweight, since
  your code only uses these for the niche label right now.
- `template.png` generated for all 5 graphic skills via your existing
  `template_generator.py`, so there's a visual fallback even with the
  generative layout engine switched off.

**`layout_engine.py` — built for real this time.** The version Kimi was
sending you arrived as a base64 blob through PowerShell and never
actually landed (confirmed: `update.zip` you uploaded is 407 bytes of
HTML, not a real zip; nothing in your `main.py` referenced a layout
engine). This one:
- Sends GPT-4o-mini (JSON mode) the product description, price, and the
  chosen skill's `SKILL.md` + config as constraints.
- Every field in the response is validated and clamped — bad coordinates,
  invalid hex colors, or a wrong shape type get silently corrected rather
  than crashing the renderer.
- If the API call fails for *any* reason (bad key, network issue,
  malformed JSON), it falls back to a deterministic layout built from the
  skill's static `config.json` — same visual family, no crash, no
  downtime. This is not theoretical: I ran it in a sandbox with no
  network access to `api.openai.com`, and confirmed the fallback path
  fires cleanly and still renders a flyer. See `output/` for that test
  image if you want to look at it.

**`flyer_generator.py`** — added `create_flyer_from_layout()` which draws
from the AI-generated JSON spec. Your original `create_flyer()` method
is untouched, so nothing about the static path changed.

**`database.py`** — added a `layout_history` table (customer phone → last
5 layouts) so the engine can see what a customer's last few flyers looked
like and deliberately vary the next one, per your "don't repeat" ask.
This was added with `CREATE TABLE IF NOT EXISTS`, so your existing
`database.db` — with your 3 real customers and transaction history — was
preserved, not wiped. I copied your original `database.db` back in after
testing and confirmed the row counts are intact.

**`config.py`** — added `USE_GENERATIVE_LAYOUT` (reads from `.env`,
defaults to `true`). Set `USE_GENERATIVE_LAYOUT=false` if you ever want
to force the static templates only — useful if OpenAI is flaky and you'd
rather have consistent output than variety.

## 4. What I could NOT test here

This sandbox has no network access to `api.openai.com`, so I could not
verify what a *real* generated layout looks like — only that the
fallback behaves correctly when the API is unreachable. That's the more
important thing to get right (a broken fallback would mean any OpenAI
outage takes your whole flyer pipeline down), but you still need to test
the real path yourself.

### To test the real layout engine on your machine

```powershell
cd C:\Users\joshu\Downloads\augeo-mvp
.venv\Scripts\activate
.venv\Scripts\python.exe main.py
```

In a new window:

```powershell
curl.exe http://localhost:5000/test
```

Open the URL it returns. **Refresh 3-4 times** (or hit `/test?skill=skill-bold`,
`/test?skill=skill-urgency`, etc. to see other styles) — each call should
produce a genuinely different layout: different photo position, different
accent shapes, different price treatment, but staying within that skill's
color/taste family. If every refresh looks identical, check your server
console — it likely means the OpenAI call is failing and you're seeing
the fallback layout every time (not a bug, just not what you're testing
for). Common causes: wrong/unrotated key, or `OPENAI_API_KEY` not loaded
because `.env` wasn't renamed correctly.

## 5. Still not done (out of scope for this pass)

From your ops console, still outstanding:
- Emotional/grief guardrail (Agent 3's stated requirement — detect
  distress keywords, redirect warmly instead of pushing flyer questions)
- Agent 2 spend/balance alarms (OpenAI spend cap, Twilio balance floor)
- `skill-church`, `skill-sports` category skills
- Real Twilio/Paystack keys wired and tested (still demo-credits only)

Say the word and I'll do the guardrail + alarms next — they're the two
your ops console flagged as highest-risk to ship without.
