"""Main pipeline orchestration."""
import logging
from typing import List

from src.core.interfaces import VideoExtractor, VideoRepository
from src.core.models import VideoMetadata

logger = logging.getLogger("videodistiller")


class Pipeline:
    """Orchestrates video extraction and storage pipeline."""

    def __init__(
        self,
        extractor: VideoExtractor,
        repository: VideoRepository
    ):
        """
        Initialize pipeline.

        Args:
            extractor: Video extractor implementation
            repository: Storage repository implementation
        """
        self.extractor = extractor
        self.repository = repository

    def process_video(self, video_id: str) -> VideoMetadata:
        """
        Process a single video through the pipeline.

        Args:
            video_id: YouTube video ID

        Returns:
            Processed VideoMetadata
        """
        logger.info(f"Processing video {video_id}")

        # Extract metadata
        metadata = self.extractor.get_metadata(video_id)

        # Extract transcript
        transcript = self.extractor.get_transcript(video_id)
        metadata.transcript = transcript

        if not transcript:
            logger.warning(f"No transcript available for {video_id}")

        # Store
        self.repository.save(metadata)

        logger.info(f"✓ Saved: {metadata.title}")

        return metadata

    def process_playlist(self, playlist_id: str) -> List[VideoMetadata]:
        """
        Process all videos in a playlist.

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            List of processed VideoMetadata
        """
        logger.info(f"Processing playlist {playlist_id}")

        # Get video IDs
        video_ids = self.extractor.list_playlist_videos(playlist_id)
        logger.info(f"Found {len(video_ids)} videos in playlist")

        results = []

        for i, video_id in enumerate(video_ids, 1):
            try:
                logger.info(f"Processing {i}/{len(video_ids)}: {video_id}")
                video = self.process_video(video_id)
                results.append(video)
            except Exception as e:
                logger.error(f"Failed to process {video_id}: {e}")
                continue

        logger.info(f"Completed: {len(results)}/{len(video_ids)} videos")

        return results

    def process_channel(
        self,
        channel_id: str,
        limit: int = None
    ) -> List[VideoMetadata]:
        """
        Process videos from a channel.

        Args:
            channel_id: YouTube channel ID
            limit: Maximum number of videos to process

        Returns:
            List of processed VideoMetadata
        """
        logger.info(f"Processing channel {channel_id} (limit: {limit})")

        # Get video IDs
        video_ids = self.extractor.list_channel_videos(channel_id, limit)
        logger.info(f"Found {len(video_ids)} videos")

        results = []

        for i, video_id in enumerate(video_ids, 1):
            try:
                logger.info(f"Processing {i}/{len(video_ids)}: {video_id}")
                video = self.process_video(video_id)
                results.append(video)
            except Exception as e:
                logger.error(f"Failed to process {video_id}: {e}")
                continue

        logger.info(f"Completed: {len(results)}/{len(video_ids)} videos")

        return results
