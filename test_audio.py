from creative.audio import ElevenLabsAudioService


def test_audio_does_not_claim_to_render_without_key():
    service = ElevenLabsAudioService(api_key="")

    result = service.voiceover(
        "Welcome to our brand.",
        voice_id="test-voice",
    )

    assert result["status"] == "needs_configuration"


def test_dialogue_does_not_claim_to_render_without_key():
    service = ElevenLabsAudioService(api_key="")

    result = service.dialogue(
        [
            {
                "text": "Welcome to our store.",
                "voice_id": "voice-a",
            },
            {
                "text": "Thank you!",
                "voice_id": "voice-b",
            },
        ]
    )

    assert result["status"] == "needs_configuration"


def test_audio_service_imports():
    from creative.audio import build_audio_service

    service = build_audio_service()

    assert service is not None
