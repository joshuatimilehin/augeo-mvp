import os
from intelligence_provider import get_intelligence_provider, MockIntelligenceProvider, AnthropicFableProvider


def test_mock_provider_returns_deterministic_text():
    p = MockIntelligenceProvider()
    resp = p.analyze('Hello world')
    assert isinstance(resp, dict)
    assert 'mock-fable' in resp['text']


def test_anthropic_provider_fallbacks_to_mock_when_no_key(monkeypatch):
    # Ensure ANTHROPIC_API_KEY is unset for this test
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    p = AnthropicFableProvider()
    resp = p.analyze('Make me a short plan')
    assert isinstance(resp, dict)
    assert resp.get('metadata', {}).get('mock', True) is True


def test_get_intelligence_provider_name_selection():
    p = get_intelligence_provider('mock')
    assert isinstance(p, MockIntelligenceProvider)
    p2 = get_intelligence_provider('anthropic')
    assert isinstance(p2, AnthropicFableProvider)
