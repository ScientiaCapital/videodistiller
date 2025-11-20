"""Content analyzer for generating video summaries."""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.core.models import VideoMetadata, Transcript
from src.llm.openrouter_client import OpenRouterClient, CostTracker, UsageMetrics
from src.llm.prompts import get_template, auto_detect_template


logger = logging.getLogger(__name__)


@dataclass
class Summary:
    """Video summary with metadata."""

    video_id: str
    title: str
    channel_title: str
    summary_text: str
    template_used: str
    tokens_used: int
    cost: float
    created_at: datetime
    reading_level: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "video_id": self.video_id,
            "title": self.title,
            "channel_title": self.channel_title,
            "summary_text": self.summary_text,
            "template_used": self.template_used,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "created_at": self.created_at.isoformat(),
            "reading_level": self.reading_level
        }

    @staticmethod
    def from_dict(data: dict) -> "Summary":
        """Create Summary from dictionary."""
        return Summary(
            video_id=data["video_id"],
            title=data["title"],
            channel_title=data["channel_title"],
            summary_text=data["summary_text"],
            template_used=data["template_used"],
            tokens_used=data["tokens_used"],
            cost=data["cost"],
            created_at=datetime.fromisoformat(data["created_at"]),
            reading_level=data.get("reading_level")
        )


class ContentAnalyzer:
    """Analyzes video content and generates kid-friendly summaries."""

    def __init__(
        self,
        llm_client: OpenRouterClient,
        data_dir: Path,
        cost_tracker: Optional[CostTracker] = None
    ):
        """Initialize content analyzer.

        Args:
            llm_client: OpenRouter client for LLM calls
            data_dir: Directory containing video data
            cost_tracker: Optional cost tracker
        """
        self.llm_client = llm_client
        self.data_dir = Path(data_dir)
        self.cost_tracker = cost_tracker

        # Ensure directories exist
        self.metadata_dir = self.data_dir / "metadata"
        self.transcript_dir = self.data_dir / "transcripts"
        self.summary_dir = self.data_dir / "summaries"
        self.summary_dir.mkdir(parents=True, exist_ok=True)

    def _load_metadata(self, video_id: str) -> VideoMetadata:
        """Load video metadata from disk.

        Args:
            video_id: YouTube video ID

        Returns:
            VideoMetadata object

        Raises:
            FileNotFoundError: If metadata file doesn't exist
        """
        metadata_file = self.metadata_dir / f"{video_id}.json"

        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata not found for video {video_id}")

        with open(metadata_file, 'r') as f:
            data = json.load(f)
            return VideoMetadata.from_dict(data)

    def _load_transcript(self, video_id: str) -> str:
        """Load video transcript from disk.

        Args:
            video_id: YouTube video ID

        Returns:
            Full transcript text

        Raises:
            FileNotFoundError: If transcript file doesn't exist
        """
        transcript_file = self.transcript_dir / f"{video_id}.txt"

        if not transcript_file.exists():
            raise FileNotFoundError(f"Transcript not found for video {video_id}")

        with open(transcript_file, 'r') as f:
            return f.read()

    def _save_summary(self, summary: Summary) -> None:
        """Save summary to disk.

        Args:
            summary: Summary object to save
        """
        summary_file = self.summary_dir / f"{summary.video_id}.json"

        with open(summary_file, 'w') as f:
            json.dump(summary.to_dict(), f, indent=2)

        logger.info(f"Saved summary for {summary.video_id}")

    def summarize_video(
        self,
        video_id: str,
        template_name: Optional[str] = None,
        auto_detect: bool = True
    ) -> Summary:
        """Generate summary for a video.

        Args:
            video_id: YouTube video ID
            template_name: Specific template to use (optional)
            auto_detect: Whether to auto-detect template if not specified

        Returns:
            Summary object

        Raises:
            FileNotFoundError: If video data not found
        """
        # Load video data
        metadata = self._load_metadata(video_id)
        transcript = self._load_transcript(video_id)

        logger.info(f"Summarizing {video_id}: {metadata.title}")

        # Determine template
        if template_name:
            template = get_template(template_name)
        elif auto_detect:
            template_name = auto_detect_template(metadata.title, transcript)
            template = get_template(template_name)
            logger.info(f"Auto-detected template: {template_name}")
        else:
            template = get_template("general")
            template_name = "general"

        # Build prompt
        prompt = template.build_prompt(
            title=metadata.title,
            transcript=transcript,
            channel_title=metadata.channel_title
        )

        # Generate summary
        logger.info(f"Calling LLM to generate summary...")
        summary_text, metrics = self.llm_client.complete(
            prompt,
            max_tokens=1500,
            temperature=0.7
        )

        # Create summary object
        summary = Summary(
            video_id=video_id,
            title=metadata.title,
            channel_title=metadata.channel_title,
            summary_text=summary_text,
            template_used=template_name,
            tokens_used=metrics.total_tokens,
            cost=metrics.cost,
            created_at=datetime.now()
        )

        # Save summary
        self._save_summary(summary)

        logger.info(
            f"Summary generated: {metrics.total_tokens} tokens, "
            f"${metrics.cost:.4f} cost"
        )

        return summary

    def summarize_batch(
        self,
        video_ids: list[str],
        template_name: Optional[str] = None,
        auto_detect: bool = True,
        skip_existing: bool = True
    ) -> list[Summary]:
        """Generate summaries for multiple videos.

        Args:
            video_ids: List of YouTube video IDs
            template_name: Specific template to use (optional)
            auto_detect: Whether to auto-detect templates
            skip_existing: Skip videos that already have summaries

        Returns:
            List of Summary objects
        """
        summaries = []
        skipped = 0

        for i, video_id in enumerate(video_ids, 1):
            # Check if summary already exists
            if skip_existing:
                summary_file = self.summary_dir / f"{video_id}.json"
                if summary_file.exists():
                    logger.info(
                        f"[{i}/{len(video_ids)}] Skipping {video_id} (already summarized)"
                    )
                    skipped += 1
                    continue

            try:
                logger.info(f"[{i}/{len(video_ids)}] Processing {video_id}...")
                summary = self.summarize_video(
                    video_id,
                    template_name=template_name,
                    auto_detect=auto_detect
                )
                summaries.append(summary)

                # Log progress
                if self.cost_tracker:
                    usage = self.cost_tracker.get_usage_summary()
                    logger.info(
                        f"Budget status: ${usage['total_cost']:.2f} / "
                        f"${self.cost_tracker.max_monthly_cost:.2f} "
                        f"({usage['budget_used_percent']:.1f}%)"
                    )

            except FileNotFoundError as e:
                logger.warning(f"Skipping {video_id}: {e}")
            except Exception as e:
                logger.error(f"Error summarizing {video_id}: {e}")

        logger.info(
            f"Batch complete: {len(summaries)} summaries generated, "
            f"{skipped} skipped"
        )

        return summaries

    def get_summary(self, video_id: str) -> Optional[Summary]:
        """Load existing summary from disk.

        Args:
            video_id: YouTube video ID

        Returns:
            Summary object or None if not found
        """
        summary_file = self.summary_dir / f"{video_id}.json"

        if not summary_file.exists():
            return None

        with open(summary_file, 'r') as f:
            data = json.load(f)
            return Summary.from_dict(data)

    def list_summaries(self) -> list[str]:
        """List all video IDs that have summaries.

        Returns:
            List of video IDs
        """
        return [
            f.stem for f in self.summary_dir.glob("*.json")
        ]
