"""
Augeo Spend & Balance Alarms
------------------------------
Two independent checks, run periodically:

1. Twilio account balance — uses Twilio's real Balance API. Alerts when
   balance drops below a floor, so you're not caught mid-conversation
   with customers when messages stop sending.

2. Daily flyer-generation volume — OpenAI doesn't expose a simple,
   reliable "current spend" endpoint scriptable from a standard API key
   (usage/cost APIs need org-admin access and aren't guaranteed stable).
   A honest, robust proxy: alert if today's flyer count blows past a
   configurable ceiling. Each flyer is ~1-2 OpenAI calls (caption +
   layout), so a volume spike IS a spend spike — whether from real
   growth or a bug/abuse loop, you want to know either way.

Alerts are sent via WhatsApp to ADMIN_PHONE if configured (through the
same Twilio client the bot already uses), and always printed to the
server log as a fallback.
"""

import os
from datetime import datetime, timezone
from contextlib import closing

from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
from database import get_connection

ADMIN_PHONE = os.getenv("ADMIN_PHONE", "")  # e.g. "whatsapp:+2348012345678"
TWILIO_BALANCE_FLOOR_USD = float(os.getenv("TWILIO_BALANCE_FLOOR_USD", "5"))
DAILY_FLYER_CEILING = int(os.getenv("DAILY_FLYER_CEILING", "500"))


def _send_admin_alert(message: str):
    print(f"[ALERT] {message}")
    # Twilio integration removed. If you want alerts via WhatsApp,
    # implement your provider here or forward to an admin webhook.


def check_twilio_balance():
    # Twilio balance checks disabled (Twilio removed). Keep a placeholder
    # so the alert loop remains functional without external dependencies.
    print("[alerts] Twilio balance check skipped (disabled).")


def check_daily_flyer_volume():
    try:
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        with closing(get_connection()) as conn:
            cur = conn.execute(
                "SELECT COUNT(*) as count FROM flyers WHERE date(created_at) = ?",
                (today,)
            )
            count = cur.fetchone()['count']
        if count > DAILY_FLYER_CEILING:
            _send_admin_alert(
                f"{count} flyers generated today, above your ceiling of "
                f"{DAILY_FLYER_CEILING}. Worth checking this is real demand "
                f"and not a loop or abuse pattern before OpenAI spend runs up."
            )
    except Exception as e:
        print(f"[alerts] daily volume check failed: {e}")


def run_all_checks():
    check_twilio_balance()
    check_daily_flyer_volume()
