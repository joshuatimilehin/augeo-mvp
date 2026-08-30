from creative.audio import AudioIntelligence


def test_audio_intelligence_detects_ugc_voice_need():
    result = AudioIntelligence().analyze(
        business="Lagos skincare brand",
        product="vitamin C serum",
        objective="create a UGC ad",
        content_type="ugc_video",
    )

    assert result.required is True
    assert result.mode == "ugc_voice"
    assert result.voice_style


def test_audio_intelligence_detects_voiceover():
    result = AudioIntelligence().analyze(
        business="fashion brand",
        product="black handbag",
        objective="launch product",
        content_type="launch video",
    )

    assert result.required is True
    assert result.mode == "voiceover"


def test_audio_intelligence_can_choose_no_audio():
    result = AudioIntelligence().analyze(
        business="restaurant",
        product="jollof rice",
        objective="create a static product poster",
        content_type="graphic_design",
    )

    assert result.required is False
    assert result.mode == "none"
