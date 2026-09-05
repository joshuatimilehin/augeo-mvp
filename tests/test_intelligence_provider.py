import importlib

import config
import intelligence_provider as intel_mod


def test_default_model_prefers_astra_gpt_6_with_fable_fallback(monkeypatch):
    monkeypatch.setenv('INTELLIGENCE_DEFAULT_MODEL', 'astra-gpt-6')
    monkeypatch.setenv('INTELLIGENCE_FALLBACK_MODEL', 'claude-fable-5-1')

    importlib.reload(config)
    importlib.reload(intel_mod)

    assert config.INTELLIGENCE_DEFAULT_MODEL == 'astra-gpt-6'
    assert config.INTELLIGENCE_FALLBACK_MODEL == 'claude-fable-5-1'

    provider = intel_mod.get_intelligence_provider()
    assert provider.model == 'astra-gpt-6'
    assert provider.fallback_model == 'claude-fable-5-1'


def test_mock_provider_returns_deterministic_text():
    p = intel_mod.MockIntelligenceProvider()
    resp = p.analyze('Hello world')
    assert isinstance(resp, dict)
    assert 'mock-fable' in resp['text']


def test_anthropic_provider_fallbacks_to_mock_when_no_key(monkeypatch):
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    p = intel_mod.AnthropicFableProvider()
    resp = p.analyze('Make me a short plan')
    assert isinstance(resp, dict)
    assert resp.get('metadata', {}).get('mock', True) is True


def test_get_intelligence_provider_name_selection():
    p = intel_mod.get_intelligence_provider('mock')
    assert isinstance(p, intel_mod.MockIntelligenceProvider)
    p2 = intel_mod.get_intelligence_provider('anthropic')
    assert isinstance(p2, intel_mod.AnthropicFableProvider)
