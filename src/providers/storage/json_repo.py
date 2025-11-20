"""JSON file-based video repository."""
import json
from pathlib import Path
from typing import List, Optional

from src.core.interfaces import VideoRepository
from src.core.models import VideoMetadata


class JSONRepository(VideoRepository):
    """Store videos as JSON files."""

    def __init__(self, data_dir: Path):
        """
        Initialize JSON repository.

        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = Path(data_dir)
        self.metadata_dir = self.data_dir / "metadata"
        self.transcripts_dir = self.data_dir / "transcripts"

        # Ensure directories exist
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)

    def save(self, video: VideoMetadata) -> None:
        """Save video metadata to JSON file."""
        # Save individual video file
        video_file = self.metadata_dir / f"{video.id}.json"
        with open(video_file, 'w', encoding='utf-8') as f:
            json.dump(video.to_dict(), f, indent=2, ensure_ascii=False)

        # Update index
        self._update_index(video)

        # Save transcript separately if present
        if video.transcript:
            transcript_file = self.transcripts_dir / f"{video.id}.txt"
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(video.transcript.text)

    def find_by_id(self, video_id: str) -> Optional[VideoMetadata]:
        """Retrieve video by ID."""
        video_file = self.metadata_dir / f"{video_id}.json"

        if not video_file.exists():
            return None

        with open(video_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return VideoMetadata.from_dict(data)

    def list_all(self) -> List[VideoMetadata]:
        """List all stored videos."""
        videos = []

        for video_file in self.metadata_dir.glob("*.json"):
            if video_file.name == "videos.json":
                continue  # Skip index file

            with open(video_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            videos.append(VideoMetadata.from_dict(data))

        return videos

    def _update_index(self, video: VideoMetadata) -> None:
        """Update the videos index file."""
        index_file = self.metadata_dir / "videos.json"

        # Load existing index
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {"videos": []}

        # Update or add video entry
        video_entry = {
            "id": video.id,
            "title": video.title,
            "channel": video.channel_title,
            "published_at": video.published_at.isoformat(),
        }

        # Remove existing entry if present
        index["videos"] = [
            v for v in index["videos"] if v["id"] != video.id
        ]

        # Add new entry
        index["videos"].append(video_entry)

        # Sort by published date (newest first)
        index["videos"].sort(
            key=lambda v: v["published_at"],
            reverse=True
        )

        # Save index
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
