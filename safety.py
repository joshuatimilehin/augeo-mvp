"""
Augeo Emotional Distress Guardrail
------------------------------------
Detects when an incoming message signals serious emotional distress
(self-harm, suicidal ideation, acute crisis language) and, if so,
short-circuits the flyer flow to respond with care and point toward
real help — instead of continuing to ask about prices and delivery.

This is intentionally conservative in scope: pattern-level detection,
not a diagnosis, not a therapy bot. It pauses commerce and hands the
person somewhere real to go. Human ops should also be able to see these
flags (logged via database.log_conversation with a distinct type).
"""

import re
from typing import Optional

# Kept broad but not exhaustive by design — the goal is to catch clear,
# direct expressions of crisis, not to play word-association with every
# sad message. False negatives here are safer to iterate on than a bot
# that interrogates someone over an offhand "I want to die" (jokingly
# said about stress) with a clinical response — but true crisis language
# should always be caught.
_DISTRESS_PATTERNS = [
    r'\bkill (myself|me)\b',
    r'\bwant to die\b',
    r'\bsuicid',
    r'\bend my life\b',
    r'\bno reason to live\b',
    r'\bbetter off dead\b',
    r'\bhurt myself\b',
    r'\bself[\s-]?harm\b',
    r"\bcan'?t (go on|do this anymore|take it anymore)\b",
]

_DISTRESS_RE = re.compile('|'.join(_DISTRESS_PATTERNS), re.IGNORECASE)

NIGERIA_CRISIS_MESSAGE = (
    "I hear you, and I want to pause here — this matters more than the flyer.\n\n"
    "If you're in immediate danger, please call 112 (Nigeria's national emergency line) "
    "or go to the nearest hospital.\n\n"
    "You can also reach SURPIN (Suicide Research and Prevention Initiative), free and "
    "confidential, 24/7:\n"
    "📞 0800 0787 746\n"
    "📞 0908 021 7555\n\n"
    "Whenever you're ready, I'll be here for the flyer — no rush at all."
)


def detect_distress(text: str) -> bool:
    if not text:
        return False
    return bool(_DISTRESS_RE.search(text))


def guardrail_response() -> str:
    return NIGERIA_CRISIS_MESSAGE
