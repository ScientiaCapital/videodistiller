"""Tests for core domain models."""
from datetime import datetime
from src.core.models import VideoMetadata, Transcript, TranscriptSegment


def test_video_metadata_creation():
    """Test VideoMetadata can be created with required fields."""
    video = VideoMetadata(
        id="abc123",
        title="Test Video",
        channel="Test Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1, 12, 0, 0),
        description="Test description",
        tags=["test", "video"],
    )

    assert video.id == "abc123"
    assert video.title == "Test Video"
    assert video.duration == 300


def test_video_metadata_to_dict():
    """Test VideoMetadata serialization to dict."""
    video = VideoMetadata(
        id="abc123",
        title="Test Video",
        channel="Test Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1, 12, 0, 0),
        description="Test description",
        tags=["test"],
    )

    data = video.to_dict()

    assert data["id"] == "abc123"
    assert data["title"] == "Test Video"
    assert data["published_at"] == "2025-01-01T12:00:00"


def test_video_metadata_from_dict():
    """Test VideoMetadata deserialization from dict."""
    data = {
        "id": "abc123",
        "title": "Test Video",
        "channel": "Test Channel",
        "channel_id": "UC123",
        "duration": 300,
        "published_at": "2025-01-01T12:00:00",
        "description": "Test description",
        "tags": ["test"],
    }

    video = VideoMetadata.from_dict(data)

    assert video.id == "abc123"
    assert video.title == "Test Video"
    assert video.published_at == datetime(2025, 1, 1, 12, 0, 0)


def test_transcript_segment_creation():
    """Test TranscriptSegment can be created."""
    segment = TranscriptSegment(
        text="Hello world",
        start=0.0,
        duration=2.5
    )

    assert segment.text == "Hello world"
    assert segment.start == 0.0
    assert segment.duration == 2.5


def test_transcript_creation():
    """Test Transcript can be created with segments."""
    segments = [
        TranscriptSegment(text="Hello", start=0.0, duration=1.0),
        TranscriptSegment(text="world", start=1.0, duration=1.0),
    ]

    transcript = Transcript(
        text="Hello world",
        language="en",
        segments=segments,
        is_auto_generated=True
    )

    assert transcript.text == "Hello world"
    assert transcript.language == "en"
    assert len(transcript.segments) == 2
    assert transcript.is_auto_generated is True
