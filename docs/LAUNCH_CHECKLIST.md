# Augeo — Launch Readiness Checklist

Everything in this checklist needs to run on your machine or a host with
real network access — this sandbox can't reach api.openai.com, Twilio,
or Paystack, so none of it has been verified live. Work through it in
order; each step assumes the previous one passed.

## 1. Rotate and load your OpenAI key

- [ ] Revoke the old key at platform.openai.com (it's been exposed in chat logs)
- [ ] Generate a new one, put it in `.env` (copy from `.env.example`)
- [ ] Confirm it loads: `python3 -c "from config import OPENAI_API_KEY; print(bool(OPENAI_API_KEY))"` → should print `True`

## 2. Visual QA the generative layout engine — the main unverified piece

This is the most important step. Everything else in this build has been
tested; this hasn't, because it needs a real OpenAI call.

```powershell
python main.py
```

In a second terminal:

```powershell
curl.exe "http://localhost:5000/test?skill=skill-luxury"
```

Open the returned URL. **Refresh 4-5 times**, and repeat for
`skill-bold`, `skill-urgency`, `skill-festive`, `skill-minimal`. For each:

- [ ] Does the layout actually vary between refreshes (different photo position, accent shapes, price treatment)?
- [ ] Does it stay recognizably within that skill's palette — no red creeping into luxury, no pastels in bold?
- [ ] Is text always legible against its background (this is the thing validation/clamping can't fully guarantee — a bad color pairing can still pass all the numeric checks)?
- [ ] Check your server console for `[layout_engine] generation failed, using fallback` — if you see this on every request, the API call itself is failing (bad key, rate limit, network) and you're only looking at fallback output, not the real generative path.

If layouts look repetitive or ugly after this, the fix is almost always
in the skill's `SKILL.md` — tighten `forbidden`/`required` or add more
specific `layout_rules`, not in `layout_engine.py` itself.

## 3. Wire and test messaging for real (Kaspo or your provider)

- [ ] Add `KASPO_API_KEY` and `KASPO_BASE_URL` to `.env` (or configure your preferred messaging gateway).
- [ ] Configure `IMAGE_PROVIDER=ideogram` (default) unless you explicitly want an alternative.
- [ ] Send a test message using your messaging provider's sandbox/webhook and confirm messages posted to `/whatsapp` are received by the app (use ngrok or similar to expose localhost).
- [ ] Walk through the full flow yourself: `order` → send a photo → enter price/sizes/delivery → pick style → receive watermarked preview (captions are English by default; users may provide custom caption text).
- [ ] Reply `privacy` and `terms` — confirm you get the links and they resolve (needs `BASE_URL` set to your public URL, not `localhost`)

## 4. Wire and test Paystack for real

- [ ] Add real `PAYSTACK_SECRET_KEY` to `.env`
- [ ] Set your Paystack webhook URL to point at `/paystack/webhook` on your public URL
- [ ] Make one real (or Paystack test-mode) purchase of the Starter pack
- [ ] Confirm credits actually land on your test account after payment
- [ ] Trigger a webhook with mismatched/missing metadata deliberately (or just trust the fix) and confirm the server doesn't crash — this was the dead-code bug that's now fixed, worth confirming it stays fixed

## 5. Confirm the alarms actually fire

- [ ] Set `ADMIN_PHONE` in `.env` to your own WhatsApp number (format: `whatsapp:+234...`)
- [ ] Temporarily set `TWILIO_BALANCE_FLOOR_USD` above your actual balance and confirm you get an alert within 30 minutes
- [ ] Set it back to a sane floor (e.g. `5`) once confirmed

## 6. Compliance basics

- [ ] `/privacy` and `/terms` resolve at your public `BASE_URL`
- [ ] Read through `docs/PRIVACY_NOTICE.md` and `docs/TERMS_AND_REFUNDS.md` yourself and adjust anything that doesn't match how you actually plan to run things (the refund window, what counts as "our-side error", etc. are starting defaults, not fixed rules)

## 7. Soft launch

- [ ] 5-10 people you know personally, not strangers — watch every message they send for confusion points in the conversation flow
- [ ] Check `originality_flags` and `layout_history` tables after — anything flagged?
- [ ] Only after this: wider referral-based seeding, per the feasibility study's 90-day recommendations
