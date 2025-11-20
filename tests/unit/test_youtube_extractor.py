"""Tests for YouTube extractor."""
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Create mock classes that inherit from proper base classes
class MockHttpError(Exception):
    """Mock HttpError for testing."""
    def __init__(self, resp, content):
        self.resp = resp
        self.content = content
        super().__init__(str(content))

# Mock the external dependencies before importing the extractor
mock_googleapiclient = MagicMock()
mock_googleapiclient_discovery = MagicMock()
mock_googleapiclient_errors = MagicMock()
mock_googleapiclient_errors.HttpError = MockHttpError

sys.modules['googleapiclient'] = mock_googleapiclient
sys.modules['googleapiclient.discovery'] = mock_googleapiclient_discovery
sys.modules['googleapiclient.errors'] = mock_googleapiclient_errors
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


def test_youtube_extractor_quota_exceeded():
    """Test YouTubeExtractor raises QuotaExceeded on 403 error."""
    with patch('src.providers.youtube.extractor.build') as mock_build:
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube

        # Mock the response object
        mock_resp = Mock()
        mock_resp.status = 403

        # Create HttpError using our MockHttpError
        http_error = MockHttpError(mock_resp, b'Quota exceeded')

        mock_youtube.videos().list().execute.side_effect = http_error

        extractor = YouTubeExtractor(api_key="test_key")

        try:
            extractor.get_metadata("abc123")
            assert False, "Should raise QuotaExceeded"
        except QuotaExceeded as e:
            assert "quota exceeded" in str(e).lower()


def test_youtube_extractor_list_playlist_videos():
    """Test YouTubeExtractor lists playlist videos."""
    with patch('src.providers.youtube.extractor.build') as mock_build:
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube

        # Mock paginated API response
        mock_youtube.playlistItems().list().execute.side_effect = [
            {
                'items': [
                    {'contentDetails': {'videoId': 'video1'}},
                    {'contentDetails': {'videoId': 'video2'}},
                ],
                'nextPageToken': 'token123'
            },
            {
                'items': [
                    {'contentDetails': {'videoId': 'video3'}},
                ],
                # No nextPageToken means last page
            }
        ]

        extractor = YouTubeExtractor(api_key="test_key")
        video_ids = extractor.list_playlist_videos("PL123")

        assert len(video_ids) == 3
        assert video_ids == ['video1', 'video2', 'video3']


def test_youtube_extractor_list_channel_videos():
    """Test YouTubeExtractor lists channel videos."""
    with patch('src.providers.youtube.extractor.build') as mock_build:
        mock_youtube = Mock()
        mock_build.return_value = mock_youtube

        # Mock API response
        mock_youtube.search().list().execute.return_value = {
            'items': [
                {'id': {'videoId': 'video1'}},
                {'id': {'videoId': 'video2'}},
                {'id': {'videoId': 'video3'}},
            ],
            # No nextPageToken means last page
        }

        extractor = YouTubeExtractor(api_key="test_key")
        video_ids = extractor.list_channel_videos("UC123", limit=3)

        assert len(video_ids) == 3
        assert video_ids == ['video1', 'video2', 'video3']
