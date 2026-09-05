import os
import json
from payment_provider import get_payment_provider, MockPaymentProvider, PaystackProvider


def test_get_mock_provider_by_name():
    p = get_payment_provider('mock')
    assert isinstance(p, MockPaymentProvider)


def test_paystack_provider_signature(monkeypatch):
    # Ensure PAYSTACK_SECRET_KEY is set for this test
    monkeypatch.setenv('PAYSTACK_SECRET_KEY', 'secret-key-123')
    p = PaystackProvider(secret='secret-key-123')
    payload = b'{"event":"charge.success","data":{"id":"abc"}}'
    # compute expected signature
    import hmac, hashlib
    expected = hmac.new(b'secret-key-123', payload, hashlib.sha512).hexdigest()
    assert p.verify_signature(payload, expected) is True
    assert p.parse_event(payload)['event'] == 'charge.success'


def test_get_payment_provider_defaults_to_paystack_or_mock(monkeypatch):
    # Unset PAYSTACK_SECRET_KEY to simulate local dev
    monkeypatch.delenv('PAYSTACK_SECRET_KEY', raising=False)
    p = get_payment_provider('paystack')
    # Should be an instance of PaystackProvider even if no secret set; verification will fail without key
    assert isinstance(p, PaystackProvider)
