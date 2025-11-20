"""Tests for core domain models."""
from datetime import datetime
from src.core.models import VideoMetadata, Transcript, TranscriptSegment


def test_video_metadata_creation():
    """Test VideoMetadata can be created with required fields."""
    video = VideoMetadata(
        id="abc123",
        title="Test Video",
        channel_title="Test Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1, 12, 0, 0),
        description="Test description",
        tags=["test", "video"],
        view_count=1000,
        like_count=50,
        comment_count=10,
        thumbnail_url="https://example.com/thumb.jpg",
    )

    assert video.id == "abc123"
    assert video.title == "Test Video"
    assert video.duration == 300
    assert video.view_count == 1000
    assert video.like_count == 50
    assert video.comment_count == 10
    assert video.thumbnail_url == "https://example.com/thumb.jpg"


def test_video_metadata_to_dict():
    """Test VideoMetadata serialization to dict."""
    video = VideoMetadata(
        id="abc123",
        title="Test Video",
        channel_title="Test Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1, 12, 0, 0),
        description="Test description",
        tags=["test"],
        view_count=1000,
        like_count=50,
        comment_count=10,
        thumbnail_url="https://example.com/thumb.jpg",
    )

    data = video.to_dict()

    assert data["id"] == "abc123"
    assert data["title"] == "Test Video"
    assert data["channel_title"] == "Test Channel"
    assert data["published_at"] == "2025-01-01T12:00:00"
    assert data["view_count"] == 1000
    assert data["like_count"] == 50
    assert data["comment_count"] == 10
    assert data["thumbnail_url"] == "https://example.com/thumb.jpg"
    assert "extracted_at" in data


def test_video_metadata_from_dict():
    """Test VideoMetadata deserialization from dict."""
    data = {
        "id": "abc123",
        "title": "Test Video",
        "channel_title": "Test Channel",
        "channel_id": "UC123",
        "duration": 300,
        "published_at": "2025-01-01T12:00:00",
        "description": "Test description",
        "tags": ["test"],
        "view_count": 1000,
        "like_count": 50,
        "comment_count": 10,
        "thumbnail_url": "https://example.com/thumb.jpg",
        "extracted_at": "2025-01-15T10:30:00",
    }

    video = VideoMetadata.from_dict(data)

    assert video.id == "abc123"
    assert video.title == "Test Video"
    assert video.channel_title == "Test Channel"
    assert video.published_at == datetime(2025, 1, 1, 12, 0, 0)
    assert video.view_count == 1000
    assert video.like_count == 50
    assert video.comment_count == 10
    assert video.thumbnail_url == "https://example.com/thumb.jpg"
    assert video.extracted_at == datetime(2025, 1, 15, 10, 30, 0)


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
        video_id="abc123",
        text="Hello world",
        language="en",
        segments=segments,
        is_auto_generated=True
    )

    assert transcript.video_id == "abc123"
    assert transcript.text == "Hello world"
    assert transcript.language == "en"
    assert len(transcript.segments) == 2
    assert transcript.is_auto_generated is True


def test_transcript_to_dict():
    """Test Transcript serialization to dict includes video_id."""
    segments = [
        TranscriptSegment(text="Hello", start=0.0, duration=1.0),
    ]

    transcript = Transcript(
        video_id="abc123",
        text="Hello",
        language="en",
        segments=segments,
        is_auto_generated=True
    )

    data = transcript.to_dict()

    assert data["video_id"] == "abc123"
    assert data["text"] == "Hello"
    assert data["language"] == "en"
    assert data["is_auto_generated"] is True


def test_transcript_from_dict():
    """Test Transcript deserialization from dict includes video_id."""
    data = {
        "video_id": "abc123",
        "text": "Hello",
        "language": "en",
        "segments": [
            {"text": "Hello", "start": 0.0, "duration": 1.0}
        ],
        "is_auto_generated": True
    }

    transcript = Transcript.from_dict(data)

    assert transcript.video_id == "abc123"
    assert transcript.text == "Hello"
    assert transcript.language == "en"
    assert transcript.is_auto_generated is True
