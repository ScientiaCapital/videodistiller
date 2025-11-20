"""Tests for JSON repository."""
from datetime import datetime
from pathlib import Path
from src.core.models import VideoMetadata
from src.providers.storage.json_repo import JSONRepository


def test_json_repository_save_video(tmp_path):
    """Test JSONRepository saves video metadata."""
    repo = JSONRepository(data_dir=tmp_path)
    video = VideoMetadata(
        id="abc123",
        title="Test Video",
        channel_title="Test Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1),
        description="Test",
        tags=["test"]
    )

    repo.save(video)

    # Check video file exists
    video_file = tmp_path / "metadata" / "abc123.json"
    assert video_file.exists()

    # Check index updated
    index_file = tmp_path / "metadata" / "videos.json"
    assert index_file.exists()


def test_json_repository_find_by_id(tmp_path):
    """Test JSONRepository retrieves video by ID."""
    repo = JSONRepository(data_dir=tmp_path)
    video = VideoMetadata(
        id="abc123",
        title="Test Video",
        channel_title="Test Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1),
        description="Test",
        tags=[]
    )

    repo.save(video)
    found = repo.find_by_id("abc123")

    assert found is not None
    assert found.id == "abc123"
    assert found.title == "Test Video"


def test_json_repository_find_nonexistent(tmp_path):
    """Test JSONRepository returns None for missing video."""
    repo = JSONRepository(data_dir=tmp_path)

    found = repo.find_by_id("nonexistent")

    assert found is None


def test_json_repository_list_all(tmp_path):
    """Test JSONRepository lists all videos."""
    repo = JSONRepository(data_dir=tmp_path)

    video1 = VideoMetadata(
        id="abc123",
        title="Video 1",
        channel_title="Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1),
        description="Test",
        tags=[]
    )
    video2 = VideoMetadata(
        id="def456",
        title="Video 2",
        channel_title="Channel",
        channel_id="UC123",
        duration=600,
        published_at=datetime(2025, 1, 2),
        description="Test",
        tags=[]
    )

    repo.save(video1)
    repo.save(video2)

    all_videos = repo.list_all()

    assert len(all_videos) == 2
    assert {v.id for v in all_videos} == {"abc123", "def456"}
