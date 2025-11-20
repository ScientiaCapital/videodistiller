"""Abstract interfaces for provider plugins."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.core.models import Transcript, VideoMetadata


class VideoExtractor(ABC):
    """Interface for video metadata and transcript extraction."""

    @abstractmethod
    def get_metadata(self, video_id: str) -> VideoMetadata:
        """
        Fetch video metadata from YouTube.

        Args:
            video_id: YouTube video ID

        Returns:
            VideoMetadata object

        Raises:
            VideoNotFound: If video doesn't exist or is private
            QuotaExceeded: If YouTube API quota exceeded
        """
        pass

    @abstractmethod
    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        """
        Fetch video transcript.

        Args:
            video_id: YouTube video ID

        Returns:
            Transcript object or None if not available
        """
        pass

    @abstractmethod
    def list_playlist_videos(self, playlist_id: str) -> List[str]:
        """
        Get all video IDs in a playlist.

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            List of video IDs
        """
        pass

    @abstractmethod
    def list_channel_videos(
        self,
        channel_id: str,
        limit: Optional[int] = None
    ) -> List[str]:
        """
        Get recent videos from a channel.

        Args:
            channel_id: YouTube channel ID
            limit: Maximum number of videos to return

        Returns:
            List of video IDs
        """
        pass


class VideoRepository(ABC):
    """Interface for video storage."""

    @abstractmethod
    def save(self, video: VideoMetadata) -> None:
        """
        Save video metadata.

        Args:
            video: VideoMetadata object to save
        """
        pass

    @abstractmethod
    def find_by_id(self, video_id: str) -> Optional[VideoMetadata]:
        """
        Retrieve video by ID.

        Args:
            video_id: YouTube video ID

        Returns:
            VideoMetadata object or None if not found
        """
        pass

    @abstractmethod
    def list_all(self) -> List[VideoMetadata]:
        """
        List all stored videos.

        Returns:
            List of VideoMetadata objects
        """
        pass
