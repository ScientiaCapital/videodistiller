"""Tests for YouTube extractor."""
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Mock the external dependencies before importing the extractor
sys.modules['googleapiclient'] = MagicMock()
sys.modules['googleapiclient.discovery'] = MagicMock()
sys.modules['googleapiclient.errors'] = MagicMock()
sys.modules['youtube_transcript_api'] = MagicMock()
sys.modules['youtube_transcript_api._errors'] = MagicMock()

from src.providers.youtube.extractor import YouTubeExtractor
from src.providers.youtube.exceptions import VideoNotFound, QuotaExceeded


def test_youtube_extractor_get_metadata():
    """Test YouTubeExtractor fetches video metadata."""
    with patch('src.providers.youtube.extractor.build') as mock_build:
        # Mock YouTube API response
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube

        mock_youtube.videos().list().execute.return_value = {
            'items': [{
                'id': 'abc123',
                'snippet': {
                    'title': 'Test Video',
                    'channelTitle': 'Test Channel',
                    'channelId': 'UC123',
                    'description': 'Test description',
                    'publishedAt': '2025-01-01T12:00:00Z',
                    'tags': ['test', 'video']
                },
                'contentDetails': {
                    'duration': 'PT5M30S'  # ISO 8601 duration
                }
            }]
        }

        extractor = YouTubeExtractor(api_key="test_key")
        metadata = extractor.get_metadata("abc123")

        assert metadata.id == "abc123"
        assert metadata.title == "Test Video"
        assert metadata.channel_title == "Test Channel"
        assert metadata.duration == 330  # 5 min 30 sec


def test_youtube_extractor_video_not_found():
    """Test YouTubeExtractor raises error for missing video."""
    with patch('src.providers.youtube.extractor.build') as mock_build:
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube

        mock_youtube.videos().list().execute.return_value = {
            'items': []
        }

        extractor = YouTubeExtractor(api_key="test_key")

        try:
            extractor.get_metadata("nonexistent")
            assert False, "Should raise VideoNotFound"
        except VideoNotFound:
            pass


def test_youtube_extractor_get_transcript():
    """Test YouTubeExtractor fetches transcript."""
    with patch('src.providers.youtube.extractor.YouTubeTranscriptApi') as mock_transcript_api:
        mock_transcript_api.get_transcript.return_value = [
            {'text': 'Hello', 'start': 0.0, 'duration': 1.0},
            {'text': 'world', 'start': 1.0, 'duration': 1.0},
        ]

        extractor = YouTubeExtractor(api_key="test_key")
        transcript = extractor.get_transcript("abc123")

        assert transcript is not None
        assert transcript.text == "Hello world"
        assert len(transcript.segments) == 2
        assert transcript.segments[0].text == "Hello"
