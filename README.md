# Augeo

Augeo is a conversational creative studio for product businesses. Send or tag Augeo with a product request; it gathers the missing context, uses the saved brand profile, and returns creative made to sell the product.

## What it does

- Product graphics and social ads
- Product UGC MP4s from a reference/product image
- Product launch videos and motion graphics
- Captions and five-day content plans

The public product does not create websites, PDFs, games, or code.

## Conversation flow

```text
Product request → product / offer / audience / channel → creative route → render job → delivery
```

For graphics, Augeo collects a product image, offer/price, and intended channel. For product UGC, it requires a clean product or reference image so the video is grounded in the real item rather than a generic substitute.

## Video setup

Runway is the default renderer. Copy `.env.example` to `.env` and set:

```env
VIDEO_PROVIDER=runway
RUNWAYML_API_SECRET=your_runway_secret
RUNWAY_VIDEO_MODEL=gen4.5
```

OpenAI video remains available by setting `VIDEO_PROVIDER=openai` and `OPENAI_API_KEY`.

`POST /agent/execute` accepts an instruction and optional context. Include `context.assets` for a product/reference image and `context.customer_phone` to attach saved brand context and receive WhatsApp render updates.

```json
{
  "instruction": "@Augeo make UGC for my new sandals",
  "context": {
    "assets": ["https://example.com/sandals.jpg"],
    "customer_phone": "+234..."
  }
}
```

Use `GET /agent/video/<video_id>` to check progress and `GET /agent/video/<video_id>/content` to retrieve a completed MP4.

## Run locally

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe main.py
```
