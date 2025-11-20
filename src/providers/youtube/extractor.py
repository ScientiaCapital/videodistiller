"""YouTube video extractor using YouTube Data API v3."""
import re
from datetime import datetime
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

from src.core.interfaces import VideoExtractor
from src.core.models import VideoMetadata, Transcript, TranscriptSegment
from src.providers.youtube.exceptions import (
    VideoNotFound,
    QuotaExceeded
)


class YouTubeExtractor(VideoExtractor):
    """Extract video metadata and transcripts from YouTube."""

    def __init__(self, api_key: str):
        """
        Initialize YouTube extractor.

        Args:
            api_key: YouTube Data API v3 key
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_metadata(self, video_id: str) -> VideoMetadata:
        """Fetch video metadata from YouTube API."""
        try:
            response = self.youtube.videos().list(
                part='snippet,contentDetails',
                id=video_id
            ).execute()

            if not response['items']:
                raise VideoNotFound(f"Video {video_id} not found")

            item = response['items'][0]
            snippet = item['snippet']
            content = item['contentDetails']

            return VideoMetadata(
                id=video_id,
                title=snippet['title'],
                channel_title=snippet['channelTitle'],
                channel_id=snippet['channelId'],
                duration=self._parse_duration(content['duration']),
                published_at=datetime.fromisoformat(
                    snippet['publishedAt'].replace('Z', '+00:00')
                ),
                description=snippet.get('description', ''),
                tags=snippet.get('tags', [])
            )

        except HttpError as e:
            if e.resp.status == 403:
                raise QuotaExceeded("YouTube API quota exceeded")
            raise

    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        """Fetch video transcript."""
        try:
            # Get transcript (auto-generated or manual)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

            # Combine into full text
            full_text = ' '.join(entry['text'] for entry in transcript_list)

            # Create segments
            segments = [
                TranscriptSegment(
                    text=entry['text'],
                    start=entry['start'],
                    duration=entry['duration']
                )
                for entry in transcript_list
            ]

            return Transcript(
                video_id=video_id,
                text=full_text,
                language='en',  # Default, could be detected
                segments=segments,
                is_auto_generated=True  # Could check this
            )

        except Exception:
            # No transcript available (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable)
            return None

    def list_playlist_videos(self, playlist_id: str) -> List[str]:
        """Get all video IDs in a playlist."""
        video_ids = []
        next_page_token = None

        while True:
            try:
                response = self.youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()

                video_ids.extend([
                    item['contentDetails']['videoId']
                    for item in response['items']
                ])

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            except HttpError as e:
                if e.resp.status == 403:
                    raise QuotaExceeded("YouTube API quota exceeded")
                raise

        return video_ids

    def list_channel_videos(
        self,
        channel_id: str,
        limit: Optional[int] = None
    ) -> List[str]:
        """Get recent videos from a channel."""
        video_ids = []
        next_page_token = None

        try:
            while True:
                response = self.youtube.search().list(
                    part='id',
                    channelId=channel_id,
                    type='video',
                    order='date',
                    maxResults=min(50, limit) if limit else 50,
                    pageToken=next_page_token
                ).execute()

                video_ids.extend([
                    item['id']['videoId']
                    for item in response['items']
                ])

                if limit and len(video_ids) >= limit:
                    video_ids = video_ids[:limit]
                    break

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

        except HttpError as e:
            if e.resp.status == 403:
                raise QuotaExceeded("YouTube API quota exceeded")
            raise

        return video_ids

    @staticmethod
    def _parse_duration(duration_str: str) -> int:
        """
        Parse ISO 8601 duration to seconds.

        Args:
            duration_str: ISO 8601 duration (e.g., 'PT5M30S')

        Returns:
            Duration in seconds
        """
        # Parse PT5M30S format
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds
