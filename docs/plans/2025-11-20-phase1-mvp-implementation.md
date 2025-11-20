# VideoDistiller Phase 1 MVP - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI tool to extract YouTube video metadata and transcripts, storing them as organized JSON files.

**Architecture:** Modular pipeline with plugin providers (YouTube API, JSON storage) and clear separation between domain models, business logic, and infrastructure. Uses Strategy and Repository patterns for extensibility.

**Tech Stack:** Python 3.10+, Click (CLI), Pydantic (validation), google-api-python-client (YouTube API), youtube-transcript-api (transcripts), pytest (testing)

---

## Prerequisites

- Python 3.10 or higher installed
- YouTube Data API v3 key (get from Google Cloud Console)
- Working directory: `/Users/tmkipper/Desktop/tk_projects/videodistiller`

---

## Task 1: Project Setup & Dependencies

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `requirements.txt`
- Create: `README.md`
- Create: `QUICKSTART.md`

### Step 1: Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "videodistiller"
version = "0.1.0"
description = "Extract and analyze YouTube video content"
readme = "README.md"
requires-python = ">=3.10"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
dependencies = [
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "google-api-python-client>=2.100.0",
    "youtube-transcript-api>=0.6.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "black>=23.10.0",
    "ruff>=0.1.0",
]

[project.scripts]
videodistiller = "src.cli.main:cli"

[tool.black]
line-length = 88
target-version = ['py310']

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
```

### Step 2: Create .env.example

```env
# YouTube Data API v3
YOUTUBE_API_KEY=your_youtube_api_key_here

# Data Storage
DATA_DIR=./data
LOG_DIR=./logs
LOG_LEVEL=INFO

# Rate Limits
YOUTUBE_REQUESTS_PER_SECOND=10
```

### Step 3: Create requirements.txt

```txt
click>=8.1.0
pydantic>=2.0.0
python-dotenv>=1.0.0
google-api-python-client>=2.100.0
youtube-transcript-api>=0.6.0
rich>=13.0.0

# Dev dependencies
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
black>=23.10.0
ruff>=0.1.0
```

### Step 4: Create README.md

```markdown
# VideoDistiller

A powerful pipeline for extracting, processing, and analyzing video content from YouTube.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure YouTube API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your YOUTUBE_API_KEY
   ```

3. Validate setup:
   ```bash
   python validate_setup.py
   ```

4. Extract a video:
   ```bash
   videodistiller extract --url "https://youtube.com/watch?v=..."
   ```

## Features

- Extract video metadata from YouTube URLs
- Download transcripts (auto-generated or manual)
- Process entire playlists and channels
- Store data in organized JSON format

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## Project Structure

```
videodistiller/
├── src/              # Source code
├── tests/            # Tests
├── data/             # Extracted data (created at runtime)
├── logs/             # Application logs (created at runtime)
└── docs/             # Documentation
```
```

### Step 5: Create QUICKSTART.md

```markdown
# VideoDistiller - Quick Start Guide

Get VideoDistiller running in 10 minutes.

## Step 1: Prerequisites

- Python 3.10 or higher
- pip package manager
- YouTube Data API v3 key

## Step 2: Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "YouTube Data API v3"
4. Create credentials → API Key
5. Copy the API key

## Step 3: Install

```bash
# Clone or navigate to project
cd videodistiller

# Install dependencies
pip install -r requirements.txt

# Or use pip install -e . for development
pip install -e ".[dev]"
```

## Step 4: Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# YOUTUBE_API_KEY=your_key_here
```

## Step 5: Validate

```bash
python validate_setup.py
```

Expected output:
```
✓ YouTube API key configured
✓ Data directory writable
✓ Dependencies installed
✓ Setup validated successfully!
```

## Step 6: Extract Your First Video

```bash
# Single video
videodistiller extract --url "https://youtube.com/watch?v=dQw4w9WgXcQ"

# Playlist
videodistiller extract --playlist "https://youtube.com/playlist?list=PLxxx"

# Channel (recent 10 videos)
videodistiller extract --channel "UCxxx" --limit 10
```

## What Gets Created

```
data/
├── metadata/
│   ├── videos.json           # Index of all videos
│   └── VIDEO_ID.json         # Individual video metadata
└── transcripts/
    └── VIDEO_ID.txt          # Raw transcript text

logs/
└── videodistiller.log        # Application logs
```

## Troubleshooting

**"Quota exceeded" error:**
- YouTube API has daily quota limits
- Wait 24 hours or increase quota in Google Cloud Console

**"No transcript available" warning:**
- Some videos don't have transcripts
- VideoDistiller will save metadata only

**"Private video" warning:**
- Private videos are skipped automatically
- This is expected behavior
```

### Step 6: Install dependencies

Run:
```bash
pip install -r requirements.txt
```

Expected: All packages install successfully

### Step 7: Commit

```bash
git add pyproject.toml requirements.txt .env.example README.md QUICKSTART.md
git commit -m "feat: add project configuration and documentation

- Add pyproject.toml with dependencies
- Add .env.example template
- Add README and QUICKSTART guides

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Core Domain Models

**Files:**
- Create: `src/__init__.py`
- Create: `src/core/__init__.py`
- Create: `src/core/models.py`
- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/unit/test_models.py`

### Step 1: Write the failing test

Create `tests/unit/test_models.py`:

```python
"""Tests for core domain models."""
from datetime import datetime
from src.core.models import VideoMetadata, Transcript, TranscriptSegment


def test_video_metadata_creation():
    """Test VideoMetadata can be created with required fields."""
    video = VideoMetadata(
        id="abc123",
        title="Test Video",
        channel="Test Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1, 12, 0, 0),
        description="Test description",
        tags=["test", "video"],
    )

    assert video.id == "abc123"
    assert video.title == "Test Video"
    assert video.duration == 300


def test_video_metadata_to_dict():
    """Test VideoMetadata serialization to dict."""
    video = VideoMetadata(
        id="abc123",
        title="Test Video",
        channel="Test Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1, 12, 0, 0),
        description="Test description",
        tags=["test"],
    )

    data = video.to_dict()

    assert data["id"] == "abc123"
    assert data["title"] == "Test Video"
    assert data["published_at"] == "2025-01-01T12:00:00"


def test_video_metadata_from_dict():
    """Test VideoMetadata deserialization from dict."""
    data = {
        "id": "abc123",
        "title": "Test Video",
        "channel": "Test Channel",
        "channel_id": "UC123",
        "duration": 300,
        "published_at": "2025-01-01T12:00:00",
        "description": "Test description",
        "tags": ["test"],
    }

    video = VideoMetadata.from_dict(data)

    assert video.id == "abc123"
    assert video.title == "Test Video"
    assert video.published_at == datetime(2025, 1, 1, 12, 0, 0)


def test_transcript_segment_creation():
    """Test TranscriptSegment can be created."""
    segment = TranscriptSegment(
        text="Hello world",
        start=0.0,
        duration=2.5
    )

    assert segment.text == "Hello world"
    assert segment.start == 0.0
    assert segment.duration == 2.5


def test_transcript_creation():
    """Test Transcript can be created with segments."""
    segments = [
        TranscriptSegment(text="Hello", start=0.0, duration=1.0),
        TranscriptSegment(text="world", start=1.0, duration=1.0),
    ]

    transcript = Transcript(
        text="Hello world",
        language="en",
        segments=segments,
        is_auto_generated=True
    )

    assert transcript.text == "Hello world"
    assert transcript.language == "en"
    assert len(transcript.segments) == 2
    assert transcript.is_auto_generated is True
```

### Step 2: Run test to verify it fails

Run:
```bash
pytest tests/unit/test_models.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.core.models'`

### Step 3: Create empty __init__.py files

Create `src/__init__.py`:
```python
"""VideoDistiller - YouTube video extraction and analysis."""
__version__ = "0.1.0"
```

Create `src/core/__init__.py`:
```python
"""Core domain models and interfaces."""
```

Create `tests/__init__.py`:
```python
"""Tests for VideoDistiller."""
```

Create `tests/unit/__init__.py`:
```python
"""Unit tests."""
```

### Step 4: Write minimal implementation

Create `src/core/models.py`:

```python
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
```

### Step 5: Run test to verify it passes

Run:
```bash
pytest tests/unit/test_models.py -v
```

Expected: All tests PASS

### Step 6: Commit

```bash
git add src/ tests/
git commit -m "feat: add core domain models

- Add VideoMetadata with serialization
- Add Transcript and TranscriptSegment models
- Add comprehensive unit tests

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Configuration Management

**Files:**
- Create: `src/utils/__init__.py`
- Create: `src/utils/config.py`
- Create: `tests/unit/test_config.py`

### Step 1: Write the failing test

Create `tests/unit/test_config.py`:

```python
"""Tests for configuration management."""
import os
from pathlib import Path
from src.utils.config import Config


def test_config_loads_from_env(monkeypatch):
    """Test Config loads values from environment."""
    monkeypatch.setenv("YOUTUBE_API_KEY", "test_key_123")
    monkeypatch.setenv("DATA_DIR", "/tmp/data")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    config = Config()

    assert config.youtube_api_key == "test_key_123"
    assert config.data_dir == Path("/tmp/data")
    assert config.log_level == "DEBUG"


def test_config_has_defaults():
    """Test Config provides sensible defaults."""
    config = Config()

    assert config.data_dir == Path("./data")
    assert config.log_dir == Path("./logs")
    assert config.log_level == "INFO"
    assert config.youtube_requests_per_second == 10


def test_config_validates_required_fields(monkeypatch):
    """Test Config raises error if required fields missing."""
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)

    config = Config()

    # Should not raise during creation
    assert config.youtube_api_key is None


def test_config_data_directory_paths():
    """Test Config provides correct directory paths."""
    config = Config()

    assert config.metadata_dir == Path("./data/metadata")
    assert config.transcripts_dir == Path("./data/transcripts")
```

### Step 2: Run test to verify it fails

Run:
```bash
pytest tests/unit/test_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.utils.config'`

### Step 3: Write minimal implementation

Create `src/utils/__init__.py`:
```python
"""Utility modules."""
```

Create `src/utils/config.py`:

```python
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
        self.data_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)
        self.transcripts_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
```

### Step 4: Run test to verify it passes

Run:
```bash
pytest tests/unit/test_config.py -v
```

Expected: All tests PASS

### Step 5: Commit

```bash
git add src/utils/ tests/unit/test_config.py
git commit -m "feat: add configuration management

- Load settings from environment variables
- Provide sensible defaults
- Add directory path helpers

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Logging Setup

**Files:**
- Create: `src/utils/logging.py`
- Create: `tests/unit/test_logging.py`

### Step 1: Write the failing test

Create `tests/unit/test_logging.py`:

```python
"""Tests for logging setup."""
import logging
from pathlib import Path
from src.utils.logging import setup_logging


def test_setup_logging_creates_logger(tmp_path):
    """Test setup_logging creates configured logger."""
    log_file = tmp_path / "test.log"

    logger = setup_logging(log_level="DEBUG", log_file=log_file)

    assert logger.name == "videodistiller"
    assert logger.level == logging.DEBUG


def test_setup_logging_writes_to_file(tmp_path):
    """Test setup_logging writes messages to file."""
    log_file = tmp_path / "test.log"

    logger = setup_logging(log_level="INFO", log_file=log_file)
    logger.info("Test message")

    assert log_file.exists()
    assert "Test message" in log_file.read_text()
```

### Step 2: Run test to verify it fails

Run:
```bash
pytest tests/unit/test_logging.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.utils.logging'`

### Step 3: Write minimal implementation

Create `src/utils/logging.py`:

```python
"""Logging configuration for VideoDistiller."""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (optional)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("videodistiller")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler (user-friendly)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(message)s"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (detailed)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger
```

### Step 4: Run test to verify it passes

Run:
```bash
pytest tests/unit/test_logging.py -v
```

Expected: All tests PASS

### Step 5: Commit

```bash
git add src/utils/logging.py tests/unit/test_logging.py
git commit -m "feat: add logging configuration

- Console handler for user-friendly output
- File handler for detailed debugging
- Configurable log levels

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Provider Interfaces

**Files:**
- Create: `src/core/interfaces.py`
- Create: `tests/unit/test_interfaces.py`

### Step 1: Write the failing test

Create `tests/unit/test_interfaces.py`:

```python
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
```

### Step 2: Run test to verify it fails

Run:
```bash
pytest tests/unit/test_interfaces.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.core.interfaces'`

### Step 3: Write minimal implementation

Create `src/core/interfaces.py`:

```python
"""Abstract interfaces for provider plugins."""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.models import VideoMetadata, Transcript


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
```

### Step 4: Run test to verify it passes

Run:
```bash
pytest tests/unit/test_interfaces.py -v
```

Expected: All tests PASS

### Step 5: Commit

```bash
git add src/core/interfaces.py tests/unit/test_interfaces.py
git commit -m "feat: add provider interfaces

- VideoExtractor for YouTube API
- VideoRepository for storage
- Abstract base classes for plugin system

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: JSON Repository Implementation

**Files:**
- Create: `src/providers/__init__.py`
- Create: `src/providers/storage/__init__.py`
- Create: `src/providers/storage/json_repo.py`
- Create: `tests/unit/test_json_repository.py`

### Step 1: Write the failing test

Create `tests/unit/test_json_repository.py`:

```python
"""Tests for JSON repository."""
from datetime import datetime
from pathlib import Path
from src.core.models import VideoMetadata
from src.providers.storage.json_repo import JSONRepository


def test_json_repository_save_video(tmp_path):
    """Test JSONRepository saves video metadata."""
    repo = JSONRepository(data_dir=tmp_path)
    video = VideoMetadata(
        id="abc123",
        title="Test Video",
        channel="Test Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1),
        description="Test",
        tags=["test"]
    )

    repo.save(video)

    # Check video file exists
    video_file = tmp_path / "metadata" / "abc123.json"
    assert video_file.exists()

    # Check index updated
    index_file = tmp_path / "metadata" / "videos.json"
    assert index_file.exists()


def test_json_repository_find_by_id(tmp_path):
    """Test JSONRepository retrieves video by ID."""
    repo = JSONRepository(data_dir=tmp_path)
    video = VideoMetadata(
        id="abc123",
        title="Test Video",
        channel="Test Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1),
        description="Test",
        tags=[]
    )

    repo.save(video)
    found = repo.find_by_id("abc123")

    assert found is not None
    assert found.id == "abc123"
    assert found.title == "Test Video"


def test_json_repository_find_nonexistent(tmp_path):
    """Test JSONRepository returns None for missing video."""
    repo = JSONRepository(data_dir=tmp_path)

    found = repo.find_by_id("nonexistent")

    assert found is None


def test_json_repository_list_all(tmp_path):
    """Test JSONRepository lists all videos."""
    repo = JSONRepository(data_dir=tmp_path)

    video1 = VideoMetadata(
        id="abc123",
        title="Video 1",
        channel="Channel",
        channel_id="UC123",
        duration=300,
        published_at=datetime(2025, 1, 1),
        description="Test",
        tags=[]
    )
    video2 = VideoMetadata(
        id="def456",
        title="Video 2",
        channel="Channel",
        channel_id="UC123",
        duration=600,
        published_at=datetime(2025, 1, 2),
        description="Test",
        tags=[]
    )

    repo.save(video1)
    repo.save(video2)

    all_videos = repo.list_all()

    assert len(all_videos) == 2
    assert {v.id for v in all_videos} == {"abc123", "def456"}
```

### Step 2: Run test to verify it fails

Run:
```bash
pytest tests/unit/test_json_repository.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.providers.storage.json_repo'`

### Step 3: Write minimal implementation

Create `src/providers/__init__.py`:
```python
"""Provider plugins."""
```

Create `src/providers/storage/__init__.py`:
```python
"""Storage provider implementations."""
```

Create `src/providers/storage/json_repo.py`:

```python
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
            "channel": video.channel,
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
```

### Step 4: Run test to verify it passes

Run:
```bash
pytest tests/unit/test_json_repository.py -v
```

Expected: All tests PASS

### Step 5: Commit

```bash
git add src/providers/ tests/unit/test_json_repository.py
git commit -m "feat: add JSON repository implementation

- Save videos as individual JSON files
- Maintain index file for quick listing
- Store transcripts separately

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: YouTube Extractor Implementation

**Files:**
- Create: `src/providers/youtube/__init__.py`
- Create: `src/providers/youtube/extractor.py`
- Create: `src/providers/youtube/exceptions.py`
- Create: `tests/unit/test_youtube_extractor.py`

### Step 1: Write the failing test

Create `tests/unit/test_youtube_extractor.py`:

```python
"""Tests for YouTube extractor."""
from unittest.mock import Mock, patch
from datetime import datetime
from src.providers.youtube.extractor import YouTubeExtractor
from src.providers.youtube.exceptions import VideoNotFound, QuotaExceeded


@patch('googleapiclient.discovery.build')
def test_youtube_extractor_get_metadata(mock_build):
    """Test YouTubeExtractor fetches video metadata."""
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
    assert metadata.channel == "Test Channel"
    assert metadata.duration == 330  # 5 min 30 sec


@patch('googleapiclient.discovery.build')
def test_youtube_extractor_video_not_found(mock_build):
    """Test YouTubeExtractor raises error for missing video."""
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


@patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript')
def test_youtube_extractor_get_transcript(mock_get_transcript):
    """Test YouTubeExtractor fetches transcript."""
    mock_get_transcript.return_value = [
        {'text': 'Hello', 'start': 0.0, 'duration': 1.0},
        {'text': 'world', 'start': 1.0, 'duration': 1.0},
    ]

    extractor = YouTubeExtractor(api_key="test_key")
    transcript = extractor.get_transcript("abc123")

    assert transcript is not None
    assert transcript.text == "Hello world"
    assert len(transcript.segments) == 2
    assert transcript.segments[0].text == "Hello"
```

### Step 2: Run test to verify it fails

Run:
```bash
pytest tests/unit/test_youtube_extractor.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.providers.youtube.extractor'`

### Step 3: Write minimal implementation

Create `src/providers/youtube/__init__.py`:
```python
"""YouTube API provider."""
```

Create `src/providers/youtube/exceptions.py`:

```python
"""Exceptions for YouTube provider."""


class VideoNotFound(Exception):
    """Raised when video doesn't exist or is private."""
    pass


class QuotaExceeded(Exception):
    """Raised when YouTube API quota is exceeded."""
    pass


class TranscriptNotAvailable(Exception):
    """Raised when transcript is not available for video."""
    pass
```

Create `src/providers/youtube/extractor.py`:

```python
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
    QuotaExceeded,
    TranscriptNotAvailable
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
                channel=snippet['channelTitle'],
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
                text=full_text,
                language='en',  # Default, could be detected
                segments=segments,
                is_auto_generated=True  # Could check this
            )

        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
            # No transcript available
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
```

### Step 4: Run test to verify it passes

Run:
```bash
pytest tests/unit/test_youtube_extractor.py -v
```

Expected: All tests PASS

### Step 5: Commit

```bash
git add src/providers/youtube/ tests/unit/test_youtube_extractor.py
git commit -m "feat: add YouTube extractor implementation

- Fetch video metadata via YouTube Data API
- Extract transcripts with youtube-transcript-api
- List playlist and channel videos
- Handle errors and quota limits

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Pipeline Implementation

**Files:**
- Create: `src/pipeline/__init__.py`
- Create: `src/pipeline/pipeline.py`
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/test_pipeline.py`

### Step 1: Write the failing test

Create `tests/integration/test_pipeline.py`:

```python
"""Integration tests for pipeline."""
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from src.core.models import VideoMetadata, Transcript, TranscriptSegment
from src.pipeline.pipeline import Pipeline
from src.providers.storage.json_repo import JSONRepository


class MockYouTubeExtractor:
    """Mock YouTube extractor for testing."""

    def get_metadata(self, video_id: str) -> VideoMetadata:
        return VideoMetadata(
            id=video_id,
            title=f"Test Video {video_id}",
            channel="Test Channel",
            channel_id="UC123",
            duration=300,
            published_at=datetime(2025, 1, 1),
            description="Test",
            tags=[]
        )

    def get_transcript(self, video_id: str) -> Transcript:
        return Transcript(
            text="Test transcript",
            language="en",
            segments=[
                TranscriptSegment(text="Test", start=0.0, duration=1.0)
            ],
            is_auto_generated=True
        )

    def list_playlist_videos(self, playlist_id: str):
        return ["video1", "video2", "video3"]

    def list_channel_videos(self, channel_id: str, limit=None):
        return ["video1", "video2"]


def test_pipeline_process_single_video(tmp_path):
    """Test Pipeline processes a single video."""
    extractor = MockYouTubeExtractor()
    repository = JSONRepository(data_dir=tmp_path)
    pipeline = Pipeline(extractor=extractor, repository=repository)

    result = pipeline.process_video("abc123")

    assert result.id == "abc123"
    assert result.title == "Test Video abc123"
    assert result.transcript is not None

    # Verify saved to repository
    saved = repository.find_by_id("abc123")
    assert saved is not None


def test_pipeline_process_playlist(tmp_path):
    """Test Pipeline processes entire playlist."""
    extractor = MockYouTubeExtractor()
    repository = JSONRepository(data_dir=tmp_path)
    pipeline = Pipeline(extractor=extractor, repository=repository)

    results = pipeline.process_playlist("PL123")

    assert len(results) == 3
    assert all(r.id in ["video1", "video2", "video3"] for r in results)

    # Verify all saved
    all_videos = repository.list_all()
    assert len(all_videos) == 3
```

### Step 2: Run test to verify it fails

Run:
```bash
pytest tests/integration/test_pipeline.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.pipeline.pipeline'`

### Step 3: Create __init__ files

Create `tests/integration/__init__.py`:
```python
"""Integration tests."""
```

### Step 4: Write minimal implementation

Create `src/pipeline/__init__.py`:
```python
"""Pipeline orchestration."""
```

Create `src/pipeline/pipeline.py`:

```python
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
```

### Step 5: Run test to verify it passes

Run:
```bash
pytest tests/integration/test_pipeline.py -v
```

Expected: All tests PASS

### Step 6: Commit

```bash
git add src/pipeline/ tests/integration/
git commit -m "feat: add pipeline orchestration

- Process single videos
- Process playlists
- Process channels with limit
- Graceful error handling

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: CLI Implementation

**Files:**
- Create: `src/cli/__init__.py`
- Create: `src/cli/main.py`
- Create: `src/cli/utils.py`

### Step 1: Write CLI main file

Create `src/cli/__init__.py`:
```python
"""Command-line interface."""
```

Create `src/cli/utils.py`:

```python
"""CLI utility functions."""
import re
from typing import Optional


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL.

    Args:
        url: YouTube URL

    Returns:
        Video ID or None if not found
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?]*)',
        r'youtube\.com/embed/([^&\n?]*)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # If no pattern matches, assume it's already a video ID
    if re.match(r'^[A-Za-z0-9_-]{11}$', url):
        return url

    return None


def extract_playlist_id(url: str) -> Optional[str]:
    """
    Extract playlist ID from YouTube URL.

    Args:
        url: YouTube URL

    Returns:
        Playlist ID or None if not found
    """
    pattern = r'list=([^&\n]*)'
    match = re.search(pattern, url)

    if match:
        return match.group(1)

    # If no pattern matches, assume it's already a playlist ID
    if url.startswith('PL') or url.startswith('UU'):
        return url

    return None
```

Create `src/cli/main.py`:

```python
"""Main CLI application."""
import sys
import click
from pathlib import Path

from src.utils.config import Config
from src.utils.logging import setup_logging
from src.providers.youtube.extractor import YouTubeExtractor
from src.providers.storage.json_repo import JSONRepository
from src.pipeline.pipeline import Pipeline
from src.cli.utils import extract_video_id, extract_playlist_id


@click.group()
def cli():
    """VideoDistiller - Extract and analyze YouTube content."""
    pass


@cli.command()
@click.option('--url', help='YouTube video URL or ID')
@click.option('--playlist', help='YouTube playlist URL or ID')
@click.option('--channel', help='YouTube channel ID')
@click.option('--limit', type=int, help='Limit number of videos (for channel)')
def extract(url, playlist, channel, limit):
    """Extract videos and transcripts from YouTube."""
    # Load configuration
    config = Config()
    config.ensure_directories_exist()

    # Setup logging
    log_file = config.log_dir / "videodistiller.log"
    logger = setup_logging(
        log_level=config.log_level,
        log_file=log_file
    )

    # Check API key
    if not config.youtube_api_key:
        click.echo("Error: YOUTUBE_API_KEY not configured in .env", err=True)
        click.echo("See QUICKSTART.md for setup instructions", err=True)
        sys.exit(1)

    # Initialize providers
    extractor = YouTubeExtractor(api_key=config.youtube_api_key)
    repository = JSONRepository(data_dir=config.data_dir)
    pipeline = Pipeline(extractor=extractor, repository=repository)

    try:
        if url:
            # Single video
            video_id = extract_video_id(url)
            if not video_id:
                click.echo(f"Error: Invalid YouTube URL: {url}", err=True)
                sys.exit(1)

            click.echo(f"Extracting video {video_id}...")
            result = pipeline.process_video(video_id)

            click.echo(f"✓ Saved: {result.title}")
            click.echo(f"  Channel: {result.channel}")
            click.echo(f"  Duration: {result.duration}s")
            if result.transcript:
                click.echo(f"  Transcript: {len(result.transcript.text)} characters")

        elif playlist:
            # Playlist
            playlist_id = extract_playlist_id(playlist)
            if not playlist_id:
                click.echo(f"Error: Invalid playlist URL: {playlist}", err=True)
                sys.exit(1)

            click.echo(f"Extracting playlist {playlist_id}...")
            results = pipeline.process_playlist(playlist_id)

            click.echo(f"\nCompleted: {len(results)} videos")

        elif channel:
            # Channel
            click.echo(f"Extracting from channel {channel}...")
            if limit:
                click.echo(f"Limit: {limit} videos")

            results = pipeline.process_channel(channel, limit)

            click.echo(f"\nCompleted: {len(results)} videos")

        else:
            click.echo("Error: Provide --url, --playlist, or --channel", err=True)
            click.echo("Run 'videodistiller extract --help' for usage", err=True)
            sys.exit(1)

    except KeyboardInterrupt:
        click.echo("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception("Extraction failed")
        sys.exit(1)


@cli.command()
def validate():
    """Validate VideoDistiller setup."""
    from src.utils.config import Config

    config = Config()
    errors = []

    # Check YouTube API key
    if not config.youtube_api_key:
        errors.append("✗ YOUTUBE_API_KEY not configured in .env")
    else:
        click.echo("✓ YouTube API key configured")

    # Check data directory
    try:
        config.ensure_directories_exist()
        click.echo("✓ Data directories created")
    except Exception as e:
        errors.append(f"✗ Cannot create data directories: {e}")

    # Check dependencies
    try:
        import googleapiclient
        import youtube_transcript_api
        click.echo("✓ Dependencies installed")
    except ImportError as e:
        errors.append(f"✗ Missing dependency: {e}")

    # Summary
    if errors:
        click.echo("\n" + "\n".join(errors))
        click.echo("\n✗ Setup validation failed")
        click.echo("See QUICKSTART.md for setup instructions")
        sys.exit(1)
    else:
        click.echo("\n✓ Setup validated successfully!")


if __name__ == '__main__':
    cli()
```

### Step 2: Test CLI manually

Run:
```bash
# Should show help
python -m src.cli.main --help

# Should show extract command help
python -m src.cli.main extract --help

# Should validate setup
python -m src.cli.main validate
```

Expected: CLI displays help and validation output

### Step 3: Make CLI executable via pip

The `pyproject.toml` already has the entry point configured. Install in development mode:

```bash
pip install -e .
```

### Step 4: Test installed command

Run:
```bash
videodistiller --help
videodistiller validate
```

Expected: CLI works via `videodistiller` command

### Step 5: Commit

```bash
git add src/cli/
git commit -m "feat: add CLI interface

- Extract command for videos, playlists, channels
- Validate command for setup verification
- User-friendly output and error handling

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: Setup Validator

**Files:**
- Create: `validate_setup.py`

### Step 1: Write validate_setup.py

Create `validate_setup.py`:

```python
#!/usr/bin/env python3
"""Validate VideoDistiller setup and configuration."""
import sys
from pathlib import Path


def check_python_version():
    """Check Python version is 3.10+."""
    if sys.version_info < (3, 10):
        print("✗ Python 3.10 or higher required")
        print(f"  Current: {sys.version}")
        return False

    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def check_dependencies():
    """Check required packages are installed."""
    required = [
        'click',
        'pydantic',
        'dotenv',
        'googleapiclient',
        'youtube_transcript_api'
    ]

    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"✗ Missing packages: {', '.join(missing)}")
        print("  Run: pip install -r requirements.txt")
        return False

    print("✓ All dependencies installed")
    return True


def check_env_file():
    """Check .env file exists."""
    env_file = Path('.env')

    if not env_file.exists():
        print("✗ .env file not found")
        print("  Run: cp .env.example .env")
        print("  Then edit .env and add your YOUTUBE_API_KEY")
        return False

    print("✓ .env file exists")
    return True


def check_api_key():
    """Check YouTube API key is configured."""
    from dotenv import load_dotenv
    import os

    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key:
        print("✗ YOUTUBE_API_KEY not configured in .env")
        print("  Add: YOUTUBE_API_KEY=your_api_key_here")
        return False

    if api_key == 'your_youtube_api_key_here':
        print("✗ YOUTUBE_API_KEY still has placeholder value")
        print("  Replace with actual API key from Google Cloud Console")
        return False

    print("✓ YouTube API key configured")
    return True


def check_directories():
    """Check data directories can be created."""
    from src.utils.config import Config

    try:
        config = Config()
        config.ensure_directories_exist()
        print("✓ Data directories created")
        return True
    except Exception as e:
        print(f"✗ Cannot create directories: {e}")
        return False


def main():
    """Run all validation checks."""
    print("VideoDistiller Setup Validation")
    print("=" * 40)
    print()

    checks = [
        check_python_version(),
        check_dependencies(),
        check_env_file(),
        check_api_key(),
        check_directories(),
    ]

    print()
    print("=" * 40)

    if all(checks):
        print("✓ Setup validated successfully!")
        print()
        print("Ready to extract videos!")
        print("Try: videodistiller extract --url 'https://youtube.com/watch?v=...'")
        return 0
    else:
        print("✗ Setup validation failed")
        print()
        print("See QUICKSTART.md for detailed setup instructions")
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

### Step 2: Make executable

Run:
```bash
chmod +x validate_setup.py
```

### Step 3: Test validator

Run:
```bash
python validate_setup.py
```

Expected: Shows validation results

### Step 4: Commit

```bash
git add validate_setup.py
git commit -m "feat: add setup validation tool

- Check Python version
- Verify dependencies installed
- Validate .env configuration
- Confirm directories can be created

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 11: Add START_HERE.txt

**Files:**
- Create: `START_HERE.txt`

### Step 1: Create START_HERE.txt

Create `START_HERE.txt`:

```
================================================================================
                           VIDEODISTILLER
                     YouTube Content Extraction Tool
================================================================================

QUICK START (10 minutes):

1. Install dependencies:
   $ pip install -r requirements.txt

2. Get YouTube API key:
   - Go to: https://console.cloud.google.com/
   - Enable "YouTube Data API v3"
   - Create API Key

3. Configure:
   $ cp .env.example .env
   $ nano .env  # Add your YOUTUBE_API_KEY

4. Validate setup:
   $ python validate_setup.py

5. Extract your first video:
   $ videodistiller extract --url "https://youtube.com/watch?v=..."

================================================================================

COMMON COMMANDS:

  Extract single video:
    $ videodistiller extract --url "https://youtube.com/watch?v=abc123"

  Extract playlist:
    $ videodistiller extract --playlist "https://youtube.com/playlist?list=PLxxx"

  Extract from channel (recent 10 videos):
    $ videodistiller extract --channel "UCxxx" --limit 10

  Validate setup:
    $ videodistiller validate

================================================================================

OUTPUT:

  Data is saved to:
    data/metadata/       - Video metadata (JSON)
    data/transcripts/    - Transcripts (text)
    logs/               - Application logs

================================================================================

DOCUMENTATION:

  - QUICKSTART.md      - Detailed 10-minute setup guide
  - README.md          - Project overview
  - docs/plans/        - Architecture and implementation docs

================================================================================

TROUBLESHOOTING:

  "Quota exceeded":
    → YouTube API has daily limits
    → Wait 24 hours or increase quota in Google Cloud Console

  "No transcript available":
    → Some videos don't have transcripts
    → VideoDistiller saves metadata only

  "YOUTUBE_API_KEY not configured":
    → Edit .env file and add your API key
    → Run: python validate_setup.py

================================================================================

For more help, see QUICKSTART.md
```

### Step 2: Commit

```bash
git add START_HERE.txt
git commit -m "docs: add START_HERE quick reference guide

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 12: Run Full Test Suite

### Step 1: Run all tests with coverage

Run:
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

Expected: All tests pass with 70%+ coverage

### Step 2: Fix any failing tests

If any tests fail, debug and fix them before proceeding.

### Step 3: Run code formatting

Run:
```bash
black src/ tests/
ruff check src/ tests/ --fix
```

Expected: Code formatted and linted

### Step 4: Commit

```bash
git add -A
git commit -m "test: ensure all tests pass with coverage

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 13: Final Integration Test

### Step 1: Create .env file

```bash
cp .env.example .env
# Manually add your YOUTUBE_API_KEY
```

### Step 2: Validate setup

Run:
```bash
python validate_setup.py
```

Expected: All checks pass

### Step 3: Test with real YouTube video (optional)

**ONLY if you have a YouTube API key configured:**

Run:
```bash
# Test with a short public video
videodistiller extract --url "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

Expected:
- Video metadata saved to `data/metadata/`
- Transcript saved to `data/transcripts/`
- No errors

### Step 4: Verify output structure

Run:
```bash
tree data/
cat data/metadata/videos.json
```

Expected: Proper directory structure with saved data

---

## Success Criteria Checklist

Phase 1 MVP is complete when all these criteria are met:

**Functional:**
- ✓ Extract metadata from YouTube video URLs
- ✓ Download transcripts (auto-generated or manual)
- ✓ Process entire playlists
- ✓ Process channel videos with limit
- ✓ Data saved as organized JSON files

**Quality:**
- ✓ Handles private videos gracefully
- ✓ Handles missing transcripts
- ✓ Respects YouTube API rate limits
- ✓ Clear error messages
- ✓ 70%+ test coverage

**Usability:**
- ✓ CLI with intuitive commands
- ✓ Progress feedback for bulk operations
- ✓ Setup validation tool
- ✓ Clear documentation (README, QUICKSTART, START_HERE)

**Documentation:**
- ✓ README.md with overview
- ✓ QUICKSTART.md with setup guide
- ✓ START_HERE.txt for quick reference
- ✓ Architecture design document

---

## Next Steps After Phase 1

**Immediate:**
1. Test with real YouTube playlists
2. Gather user feedback
3. Document any edge cases

**Phase 2 Planning:**
1. Choose LLM provider (Claude vs OpenRouter)
2. Design summarization prompts
3. Plan principle extraction logic
4. Design cost tracking

**Future Enhancements:**
1. SQLite migration for better search
2. Web UI or API
3. Background processing
4. Channel monitoring
