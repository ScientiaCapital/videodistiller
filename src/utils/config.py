"""Configuration management for VideoDistiller."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self):
        """Initialize configuration from environment."""
        # YouTube API
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")

        # Directories
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.log_dir = Path(os.getenv("LOG_DIR", "./logs"))

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # Rate limiting
        self.youtube_requests_per_second = int(
            os.getenv("YOUTUBE_REQUESTS_PER_SECOND", "10")
        )

        # LLM (OpenRouter)
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.llm_model = os.getenv("LLM_MODEL", "qwen/qwen-2.5-72b-instruct")
        self.max_monthly_cost = float(os.getenv("MAX_MONTHLY_COST", "10.0"))
        self.warn_at_cost = float(os.getenv("WARN_AT_COST", "8.0"))

    @property
    def metadata_dir(self) -> Path:
        """Directory for video metadata JSON files."""
        return self.data_dir / "metadata"

    @property
    def transcripts_dir(self) -> Path:
        """Directory for transcript text files."""
        return self.data_dir / "transcripts"

    def ensure_directories_exist(self) -> None:
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
