from creative.artifacts.artifact import CreativeArtifact


def test_creative_artifact_is_first_class():
    artifact = CreativeArtifact(
        project_id="project_123",
        artifact_type="image",
        source="mock://image",
    )

    assert artifact.id.startswith("artifact_")
    assert artifact.project_id == "project_123"
    assert artifact.artifact_type == "image"
    assert artifact.status == "created"


def test_creative_artifact_serializes():
    artifact = CreativeArtifact(
        project_id="project_123",
        artifact_type="video",
        source="mock://video",
        metadata={"duration": 30},
    )

    data = artifact.to_dict()

    assert data["artifact_type"] == "video"
    assert data["metadata"]["duration"] == 30