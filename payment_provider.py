import os
import hmac
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from config import PAYSTACK_SECRET_KEY


class PaymentProvider(ABC):
    """Abstract payment provider interface for webhook handling and verification."""

    @abstractmethod
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def parse_event(self, payload: bytes) -> Dict[str, Any]:
        raise NotImplementedError()


class MockPaymentProvider(PaymentProvider):
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        # Accept any signature that equals 'MOCK' for deterministic tests
        return signature == "MOCK"

    def parse_event(self, payload: bytes) -> Dict[str, Any]:
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception:
            return {"raw": payload.decode("utf-8", errors="replace")}


class PaystackProvider(PaymentProvider):
    """Paystack-specific verification and parsing.

    This keeps Paystack-specific logic in one place; main webhook handlers
    can use the provider abstraction to verify and parse incoming events.
    """

    def __init__(self, secret: Optional[str] = None):
        self.secret = secret or PAYSTACK_SECRET_KEY

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        if not self.secret or not signature:
            return False
        computed = hmac.new(self.secret.encode("utf-8"), payload, hashlib.sha512).hexdigest()
        return hmac.compare_digest(computed, signature)

    def parse_event(self, payload: bytes) -> Dict[str, Any]:
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception:
            return {"raw": payload.decode("utf-8", errors="replace")}


def get_payment_provider(name: Optional[str] = None) -> PaymentProvider:
    name = (name or "").lower()
    if name in ("mock", "test"):
        return MockPaymentProvider()
    if name in ("paystack", "paystack_provider") or not name:
        return PaystackProvider()
    # fallback to mock
    return MockPaymentProvider()
