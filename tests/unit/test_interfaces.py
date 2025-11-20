"""Tests for provider interfaces."""
from abc import ABC
from src.core.interfaces import VideoExtractor, VideoRepository


def test_video_extractor_is_abstract():
    """Test VideoExtractor is an abstract base class."""
    assert issubclass(VideoExtractor, ABC)


def test_video_repository_is_abstract():
    """Test VideoRepository is an abstract base class."""
    assert issubclass(VideoRepository, ABC)


def test_video_extractor_has_required_methods():
    """Test VideoExtractor defines required methods."""
    required_methods = [
        "get_metadata",
        "get_transcript",
        "list_playlist_videos",
        "list_channel_videos"
    ]

    for method in required_methods:
        assert hasattr(VideoExtractor, method)


def test_video_repository_has_required_methods():
    """Test VideoRepository defines required methods."""
    required_methods = [
        "save",
        "find_by_id",
        "list_all",
    ]

    for method in required_methods:
        assert hasattr(VideoRepository, method)
