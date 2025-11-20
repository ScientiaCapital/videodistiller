"""Integration tests for pipeline."""
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from src.core.models import VideoMetadata, Transcript, TranscriptSegment
from src.pipeline.pipeline import Pipeline
from src.providers.storage.json_repo import JSONRepository


class MockYouTubeExtractor:
    """Mock YouTube extractor for testing."""

    def get_metadata(self, video_id: str) -> VideoMetadata:
        return VideoMetadata(
            id=video_id,
            title=f"Test Video {video_id}",
            channel_title="Test Channel",
            channel_id="UC123",
            duration=300,
            published_at=datetime(2025, 1, 1),
            description="Test",
            tags=[]
        )

    def get_transcript(self, video_id: str) -> Transcript:
        return Transcript(
            video_id=video_id,
            text="Test transcript",
            language="en",
            segments=[
                TranscriptSegment(text="Test", start=0.0, duration=1.0)
            ],
            is_auto_generated=True
        )

    def list_playlist_videos(self, playlist_id: str):
        return ["video1", "video2", "video3"]

    def list_channel_videos(self, channel_id: str, limit=None):
        return ["video1", "video2"]


def test_pipeline_process_single_video(tmp_path):
    """Test Pipeline processes a single video."""
    extractor = MockYouTubeExtractor()
    repository = JSONRepository(data_dir=tmp_path)
    pipeline = Pipeline(extractor=extractor, repository=repository)

    result = pipeline.process_video("abc123")

    assert result.id == "abc123"
    assert result.title == "Test Video abc123"
    assert result.transcript is not None

    # Verify saved to repository
    saved = repository.find_by_id("abc123")
    assert saved is not None


def test_pipeline_process_playlist(tmp_path):
    """Test Pipeline processes entire playlist."""
    extractor = MockYouTubeExtractor()
    repository = JSONRepository(data_dir=tmp_path)
    pipeline = Pipeline(extractor=extractor, repository=repository)

    results = pipeline.process_playlist("PL123")

    assert len(results) == 3
    assert all(r.id in ["video1", "video2", "video3"] for r in results)

    # Verify all saved
    all_videos = repository.list_all()
    assert len(all_videos) == 3
