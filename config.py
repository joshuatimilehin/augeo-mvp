import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", BASE_DIR / "database.db")
SKILLS_PATH = Path(os.getenv("SKILLS_PATH", BASE_DIR / "skills"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

FLASK_DEBUG = os.getenv("FLASK_ENV", "production") == "development"

# Credit packs
CREDIT_PACKS = {
    "starter": {"credits": 10, "price_ngn": 3000, "label": "10 Flyers — ₦3,000"},
    "growth": {"credits": 25, "price_ngn": 6500, "label": "25 Flyers — ₦6,500 (save ₦1,000)"},
    "pro": {"credits": 60, "price_ngn": 15000, "label": "60 Flyers — ₦15,000 (save ₦3,000)"},
}

# Cost per flyer in credits
FLYER_CREDIT_COST = 1

# Brand memory threshold
BRAND_MEMORY_THRESHOLD = 3

# Generative layout engine — set to "false" in .env to force the static
# config.json layouts (e.g. if the OpenAI key is unavailable/unreliable)
USE_GENERATIVE_LAYOUT = os.getenv("USE_GENERATIVE_LAYOUT", "true").lower() != "false"
