from .elevenlabs import build_audio_service


AUDIO_INTENTS = {
    "voiceover",
    "dialogue",
    "sound_effect",
    "music",
    "transcription",
}


def infer_audio_intent(message: str) -> str | None:
    text = message.lower()

    if any(
        phrase in text
        for phrase in [
            "voiceover",
            "voice over",
            "narrate",
            "narration",
            "read this",
            "say this",
            "make this spoken",
        ]
    ):
        return "voiceover"

    if any(
        phrase in text
        for phrase in [
            "dialogue",
            "conversation",
            "two voices",
            "two people talking",
        ]
    ):
        return "dialogue"

    if any(
        phrase in text
        for phrase in [
            "sound effect",
            "sound effects",
            "sfx",
        ]
    ):
        return "sound_effect"

    if any(
        phrase in text
        for phrase in [
            "music",
            "background music",
            "soundtrack",
        ]
    ):
        return "music"

    if any(
        phrase in text
        for phrase in [
            "transcribe",
            "transcription",
            "turn this audio into text",
        ]
    ):
        return "transcription"

    return None


__all__ = [
    "AUDIO_INTENTS",
    "infer_audio_intent",
    "build_audio_service",
]
