"""Core domain models for VideoDistiller."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class TranscriptSegment:
    """Individual transcript chunk with timestamp."""
    text: str
    start: float  # seconds
    duration: float


@dataclass
class Transcript:
    """Video transcript with timestamped segments."""
    text: str
    language: str
    segments: List[TranscriptSegment]
    is_auto_generated: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "language": self.language,
            "segments": [
                {
                    "text": seg.text,
                    "start": seg.start,
                    "duration": seg.duration
                }
                for seg in self.segments
            ],
            "is_auto_generated": self.is_auto_generated
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transcript":
        """Create from dictionary."""
        segments = [
            TranscriptSegment(**seg) for seg in data["segments"]
        ]
        return cls(
            text=data["text"],
            language=data["language"],
            segments=segments,
            is_auto_generated=data["is_auto_generated"]
        )


@dataclass
class VideoMetadata:
    """Represents a YouTube video with metadata and transcript."""
    id: str
    title: str
    channel: str
    channel_id: str
    duration: int  # seconds
    published_at: datetime
    description: str
    tags: List[str] = field(default_factory=list)
    transcript: Optional[Transcript] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = {
            "id": self.id,
            "title": self.title,
            "channel": self.channel,
            "channel_id": self.channel_id,
            "duration": self.duration,
            "published_at": self.published_at.isoformat(),
            "description": self.description,
            "tags": self.tags,
        }

        if self.transcript:
            data["transcript"] = self.transcript.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VideoMetadata":
        """Create from dictionary."""
        transcript = None
        if "transcript" in data and data["transcript"]:
            transcript = Transcript.from_dict(data["transcript"])

        return cls(
            id=data["id"],
            title=data["title"],
            channel=data["channel"],
            channel_id=data["channel_id"],
            duration=data["duration"],
            published_at=datetime.fromisoformat(data["published_at"]),
            description=data["description"],
            tags=data.get("tags", []),
            transcript=transcript
        )
