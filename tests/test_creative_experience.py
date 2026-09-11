from creative.experience.director import CreativeDirector
from creative.experience.session import ExperienceSession


def test_director_understands_image_request():
    director = CreativeDirector()

    session = ExperienceSession(
        session_id="test-session"
    )

    result = director.direct(
        "Create a premium product launch visual",
        session,
    )

    assert result["intent"]["medium"] == "image"
    assert result["intent"]["goal"] == "promotion"
    assert result["intent"]["style"] == "premium"


def test_director_understands_video_request():
    director = CreativeDirector()

    session = ExperienceSession(
        session_id="test-session"
    )

    result = director.direct(
        "Create a cinematic launch video",
        session,
    )

    assert result["intent"]["medium"] == "video"
    assert result["intent"]["goal"] == "promotion"
    assert result["intent"]["style"] == "cinematic"


def test_director_creates_action_plan():
    director = CreativeDirector()

    session = ExperienceSession(
        session_id="test-session"
    )

    result = director.direct(
        "Create a luxury product image",
        session,
    )

    actions = result["plan"]["actions"]

    assert len(actions) == 1
    assert actions[0]["action_type"] == "create_image"


def test_session_remembers_conversation():
    director = CreativeDirector()

    session = ExperienceSession(
        session_id="test-session"
    )

    director.direct(
        "Create a cinematic launch video",
        session,
    )

    assert len(session.messages) == 1
    assert session.messages[0]["role"] == "user"
    assert session.current_intent is not None