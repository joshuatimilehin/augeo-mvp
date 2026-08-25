from .ideogram_describe import IdeogramDescribe
from creative.image.ideogram_describe import IdeogramDescribe

__all__ = ["IdeogramDescribe"]
def test_ideogram_describe_requires_api_key(tmp_path):
    from creative.image.ideogram_describe import IdeogramDescribe

    image = tmp_path / "reference.png"
    image.write_bytes(b"not-a-real-image")

    describe = IdeogramDescribe(api_key=None)

    try:
        describe.describe(image)
        assert False, "Expected missing API key error"
    except RuntimeError as exc:
        assert "IDEOGRAM_API_KEY" in str(exc)

        visual_dna = IdeogramDescribe().describe(reference_image)