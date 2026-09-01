import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Kaspo image provider
KASPO_API_KEY = os.getenv("KASPO_API_KEY")
KASPO_BASE_URL = os.getenv("KASPO_BASE_URL")

# Twilio removed — messages are logged locally by default
TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None
TWILIO_WHATSAPP_NUMBER = None
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", BASE_DIR / "database.db")
SKILLS_PATH = Path(os.getenv("SKILLS_PATH", BASE_DIR / "skills"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

FLASK_DEBUG = os.getenv("FLASK_ENV", "production") == "development"

# Brand voice and product boundaries
AUGEO_PERSONA = {
    "name": "Augeo",
    "voice": "confident, clear, sales-aware, and calm",
    "pricing_visibility": "hidden_in_chat_by_default",
    "default_offer_style": "offer-led, not price-led",
    "core_business": "contextual creative production for people, creators, freelancers, and businesses",
    "deliverables": ["flyers", "product visuals", "UGC videos", "launch films", "brand social content", "creative concepts"],
    "customer_types": ["creator", "freelancer", "small business", "brand"],
    "business_context_is_optional": True,
}

MEDIA_PROVIDER_PRIORITY = {
    "image": ["ideogram", "higgsfield", "legacy"],
    "video": ["runway", "seedance", "openai", "higgsfield"],
    "ugc_video": ["runway", "seedance", "openai", "higgsfield"],
    "launch_video": ["runway", "seedance", "openai", "higgsfield"],
}

DISPLAY_PRICING_IN_CHAT = False

# Credit packs
CREDIT_PACKS = {
    "starter": {"credits": 10, "price_ngn": 3000, "label": "Starter pack"},
    "growth": {"credits": 25, "price_ngn": 6500, "label": "Growth pack"},
    "pro": {"credits": 60, "price_ngn": 15000, "label": "Pro pack"},
}

# Cost per flyer in credits
FLYER_CREDIT_COST = 1

# Brand memory threshold
BRAND_MEMORY_THRESHOLD = 3

# Generative layout engine — set to "false" in .env to force the static
# config.json layouts (e.g. if the OpenAI key is unavailable/unreliable)
USE_GENERATIVE_LAYOUT = os.getenv("USE_GENERATIVE_LAYOUT", "true").lower() != "false"

IDEOGRAM_API_KEY = os.getenv('IDEOGRAM_API_KEY')
OPENAI_VIDEO_MODEL = os.getenv("OPENAI_VIDEO_MODEL", "sora-2")
VIDEO_PROVIDER = os.getenv("VIDEO_PROVIDER", "runway")
RUNWAYML_API_SECRET = os.getenv("RUNWAYML_API_SECRET")
RUNWAY_VIDEO_MODEL = os.getenv("RUNWAY_VIDEO_MODEL", "gen4.5")

# Creative video providers
SEEDANCE_API_KEY = os.getenv("SEEDANCE_API_KEY")
SEEDANCE_BASE_URL = os.getenv(
    "SEEDANCE_BASE_URL",
    "https://www.seeddance.io",
)
SEEDANCE_MODEL = os.getenv(
    "SEEDANCE_MODEL",
    "seedance-2.0",
)
