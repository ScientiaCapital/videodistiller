# VideoDistiller - Architecture Design

**Date**: 2025-11-20
**Status**: Approved
**Architecture**: Modular Pipeline with Plugins

## Overview

VideoDistiller transforms YouTube videos into a searchable knowledge base by extracting transcripts, metadata, and distilling content into core principles and actionable insights.

**Design Goals**:
- Start small (JSON storage, CLI), design for growth
- Multi-LLM support (Claude + OpenRouter for cost optimization)
- Progressive enhancement: on-demand → periodic → automated
- Clean migration path: JSON → SQLite → PostgreSQL

## Requirements

### Functional Requirements

**Phase 1 (MVP)**:
- Extract video metadata from YouTube URLs
- Download transcripts (auto-generated and manual captions)
- Process entire playlists and channel videos
- Store data in organized JSON format
- CLI interface for on-demand extraction

**Phase 2 (Future)**:
- Multi-level summarization using LLMs
- Extract core principles from technical content
- Cross-video topic analysis
- Search and query capabilities

**Phase 3 (Future)**:
- Automated monitoring of channels
- Background processing
- Web API or UI

### Non-Functional Requirements

- **Reliability**: Graceful handling of rate limits, private videos, missing transcripts
- **Cost Efficiency**: Support cheap LLMs (Qwen, DeepSeek) via OpenRouter
- **Extensibility**: Plugin architecture for providers (LLM, storage, extractors)
- **Testability**: 70%+ test coverage with mocked external dependencies
- **Usability**: Clear CLI with progress feedback

### Constraints

- ❌ NO OpenAI models (per project requirements)
- ✅ API keys must be stored in `.env` only
- ✅ Support Anthropic Claude and OpenRouter

## Architecture

### Overall Structure

**Modular Pipeline with Plugins**

```
Extract → Transform → Analyze → Store
```

**Layer Architecture**:
```
┌─────────────────────────────────────────┐
│        Interface Layer (CLI/API)        │
├─────────────────────────────────────────┤
│      Pipeline Layer (Orchestration)     │
├─────────────────────────────────────────┤
│   Provider Layer (Pluggable Backends)   │
│  - YouTube API                          │
│  - LLM Providers (Claude, OpenRouter)   │
│  - Storage (JSON, SQLite, PostgreSQL)   │
├─────────────────────────────────────────┤
│    Domain Layer (Data Models, Logic)    │
└─────────────────────────────────────────┘
```

**Design Patterns**:
- **Strategy Pattern**: Swap LLM providers via common interface
- **Repository Pattern**: Abstract storage for easy migration
- **Pipeline Pattern**: Chain processing stages with clear contracts

### Directory Structure

```
videodistiller/
├── src/
│   ├── core/                    # Domain models, interfaces
│   │   ├── __init__.py
│   │   ├── models.py            # VideoMetadata, Transcript, etc.
│   │   └── interfaces.py        # Abstract base classes
│   │
│   ├── pipeline/                # ETL stages
│   │   ├── __init__.py
│   │   ├── pipeline.py          # Main orchestrator
│   │   ├── stages.py            # Extract, Transform, Analyze, Store
│   │   └── progress.py          # Progress tracking
│   │
│   ├── providers/               # Plugins
│   │   ├── youtube/
│   │   │   ├── __init__.py
│   │   │   └── extractor.py     # YouTube API integration
│   │   ├── llm/                 # Phase 2
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # LLMProvider interface
│   │   │   ├── claude.py        # Anthropic Claude
│   │   │   └── openrouter.py    # OpenRouter gateway
│   │   └── storage/
│   │       ├── __init__.py
│   │       ├── base.py          # Repository interface
│   │       ├── json_repo.py     # JSON file storage (Phase 1)
│   │       └── sqlite_repo.py   # SQLite storage (future)
│   │
│   ├── cli/                     # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py              # Click/Typer app
│   │   └── commands.py          # CLI commands
│   │
│   └── utils/                   # Helpers
│       ├── __init__.py
│       ├── config.py            # Environment config
│       ├── logging.py           # Logging setup
│       └── retry.py             # Retry logic with backoff
│
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test data
│
├── docs/
│   ├── plans/                   # Design documents
│   └── api/                     # API reference
│
├── config/
│   └── settings.py              # Configuration schemas
│
├── data/                        # Created at runtime
│   ├── metadata/
│   ├── transcripts/
│   └── processed/               # Phase 2
│
├── logs/                        # Created at runtime
│
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Modern Python packaging
├── validate_setup.py            # Setup validator
├── README.md
├── QUICKSTART.md
└── START_HERE.txt
```

## Component Design

### 1. Domain Models

**Core Data Classes**:

```python
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
    tags: List[str]
    transcript: Optional[Transcript] = None
    summary: Optional[str] = None         # Phase 2
    principles: Optional[List[str]] = None  # Phase 2

@dataclass
class Transcript:
    """Video transcript with timestamped segments."""
    text: str
    language: str
    segments: List[TranscriptSegment]
    is_auto_generated: bool

@dataclass
class TranscriptSegment:
    """Individual transcript chunk with timestamp."""
    text: str
    start: float  # seconds
    duration: float
```

### 2. Provider Plugin System

**Abstract Interfaces**:

```python
class VideoExtractor(ABC):
    """Interface for video metadata and transcript extraction."""
    @abstractmethod
    def get_metadata(self, video_id: str) -> VideoMetadata:
        """Fetch video metadata."""

    @abstractmethod
    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        """Fetch video transcript."""

    @abstractmethod
    def list_playlist_videos(self, playlist_id: str) -> List[str]:
        """Get all video IDs in a playlist."""

    @abstractmethod
    def list_channel_videos(self, channel_id: str, limit: int) -> List[str]:
        """Get recent videos from a channel."""

class LLMProvider(ABC):
    """Interface for LLM-based analysis (Phase 2)."""
    @abstractmethod
    def summarize(self, text: str, max_length: int) -> str:
        """Generate summary of text."""

    @abstractmethod
    def extract_principles(self, transcript: str) -> List[str]:
        """Extract core principles from content."""

    @abstractmethod
    def analyze_topic(self, content: str, topic: str) -> Dict[str, Any]:
        """Analyze content for specific topic."""

class VideoRepository(ABC):
    """Interface for video storage."""
    @abstractmethod
    def save(self, video: VideoMetadata) -> None:
        """Save video metadata."""

    @abstractmethod
    def find_by_id(self, video_id: str) -> Optional[VideoMetadata]:
        """Retrieve video by ID."""

    @abstractmethod
    def list_all(self) -> List[VideoMetadata]:
        """List all stored videos."""

    @abstractmethod
    def search(self, query: str) -> List[VideoMetadata]:
        """Search videos by text query."""
```

**Implementation: YouTubeExtractor**:
- Uses `google-api-python-client` for YouTube Data API v3
- Uses `youtube-transcript-api` for transcript fetching
- Handles rate limits with exponential backoff
- Falls back from auto-generated to manual captions
- Gracefully handles private videos, missing transcripts

**Implementation: JSONRepository** (Phase 1):
- Stores each video as `data/metadata/{VIDEO_ID}.json`
- Maintains index file `data/metadata/videos.json`
- Stores transcripts separately in `data/transcripts/{VIDEO_ID}.txt`
- Simple, version-controllable, human-readable

**Future Implementations**:
- `ClaudeProvider`: Direct Anthropic API (Sonnet 4.5, Opus, Haiku)
- `OpenRouterProvider`: Unified gateway (Qwen, DeepSeek, 200+ models)
- `SQLiteRepository`: Embedded database with FTS5 search
- `PostgreSQLRepository`: Production database with vector search

### 3. Pipeline Orchestration

**Pipeline Class**:

```python
class Pipeline:
    """Orchestrates the ETL pipeline."""

    def __init__(
        self,
        extractor: VideoExtractor,
        transformer: Optional[TransformStage],
        analyzer: Optional[LLMProvider],
        repository: VideoRepository
    ):
        self.extractor = extractor
        self.transformer = transformer  # Phase 2
        self.analyzer = analyzer        # Phase 2
        self.repository = repository

    def process_video(self, video_url: str) -> VideoMetadata:
        """Process a single video through the pipeline."""
        video_id = self._extract_video_id(video_url)

        # Stage 1: Extract
        metadata = self.extractor.get_metadata(video_id)
        transcript = self.extractor.get_transcript(video_id)
        metadata.transcript = transcript

        # Stage 2: Transform (Phase 2)
        if self.transformer and transcript:
            cleaned = self.transformer.clean(transcript)
            metadata.transcript = cleaned

        # Stage 3: Analyze (Phase 2)
        if self.analyzer and transcript:
            summary = self.analyzer.summarize(transcript.text)
            principles = self.analyzer.extract_principles(transcript.text)
            metadata.summary = summary
            metadata.principles = principles

        # Stage 4: Store
        self.repository.save(metadata)

        return metadata

    def process_playlist(self, playlist_url: str) -> List[VideoMetadata]:
        """Process all videos in a playlist."""
        playlist_id = self._extract_playlist_id(playlist_url)
        video_ids = self.extractor.list_playlist_videos(playlist_id)

        results = []
        for video_id in track_progress(video_ids):
            try:
                video = self.process_video(video_id)
                results.append(video)
            except Exception as e:
                logger.error(f"Failed to process {video_id}: {e}")
                continue

        return results
```

### 4. CLI Interface

**Commands**:

```bash
# Single video
videodistiller extract --url "youtube.com/watch?v=abc123"

# Playlist
videodistiller extract --playlist "youtube.com/playlist?list=PLxxx"

# Channel (recent N videos)
videodistiller extract --channel "UCxxx" --limit 50

# Interactive mode
videodistiller interactive

# Validate setup
videodistiller validate
```

**Implementation with Click**:

```python
import click

@click.group()
def cli():
    """VideoDistiller - Extract and analyze YouTube content."""
    pass

@cli.command()
@click.option('--url', help='YouTube video URL')
@click.option('--playlist', help='YouTube playlist URL')
@click.option('--channel', help='YouTube channel ID')
@click.option('--limit', default=None, type=int, help='Limit number of videos')
def extract(url, playlist, channel, limit):
    """Extract videos and transcripts."""
    if url:
        process_single_video(url)
    elif playlist:
        process_playlist(playlist)
    elif channel:
        process_channel(channel, limit)
    else:
        click.echo("Provide --url, --playlist, or --channel")
```

## Data Flow

### Single Video Extraction

```
User runs: videodistiller extract --url "youtube.com/watch?v=abc"
    │
    ▼
CLI parses URL and extracts video_id
    │
    ▼
Pipeline.process_video(video_id)
    │
    ├─► YouTubeExtractor.get_metadata(video_id)
    │       └─► YouTube Data API v3 → VideoMetadata
    │
    ├─► YouTubeExtractor.get_transcript(video_id)
    │       ├─► Try auto-generated transcript
    │       └─► Fallback to manual captions
    │       └─► Return Transcript or None
    │
    └─► JSONRepository.save(video)
            ├─► Write data/metadata/abc.json
            ├─► Write data/transcripts/abc.txt
            └─► Update data/metadata/videos.json (index)
    │
    ▼
Success message with video title and storage location
```

### Playlist Processing

```
User runs: videodistiller extract --playlist "youtube.com/playlist?list=PLxxx"
    │
    ▼
CLI extracts playlist_id
    │
    ▼
Pipeline.process_playlist(playlist_id)
    │
    ├─► YouTubeExtractor.list_playlist_videos(playlist_id)
    │       └─► Returns [video_id1, video_id2, ...]
    │
    └─► For each video_id:
            ├─► Pipeline.process_video(video_id)
            ├─► Display progress (5/47 videos processed...)
            └─► Handle errors gracefully (skip private videos, log failures)
    │
    ▼
Summary report:
  - Processed: 43/47
  - Skipped: 4 (3 private, 1 no transcript)
  - Failed: 0
```

## Error Handling

### Common Failures and Responses

| Scenario | Detection | Response |
|----------|-----------|----------|
| **YouTube API quota exceeded** | HTTP 403 with quota error | Raise QuotaError, halt processing, notify user |
| **Rate limit hit** | HTTP 429 | Exponential backoff (3 retries: 1s, 2s, 4s) |
| **Private/deleted video** | API returns 404 or private flag | Log warning, skip video, continue pipeline |
| **No transcript available** | TranscriptNotAvailable exception | Log info, save metadata only, mark for review |
| **Network timeout** | Timeout exception | Retry with backoff (5 attempts max) |
| **Disk full** | OSError on file write | Raise critical error, halt processing |
| **Invalid API key** | HTTP 401 | Raise ConfigurationError on startup |

### Retry Strategy

**Exponential Backoff**:
```python
def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableError as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Retry {attempt+1}/{max_retries} after {delay}s")
            time.sleep(delay)
```

**Rate Limit Handling**:
- Respect `Retry-After` headers
- Global rate limiter for YouTube API (50 requests per second default)
- Per-provider rate limits for LLM APIs (Phase 2)

### Logging Strategy

**Console Output** (user-facing):
```
✓ Video 1/47: "Machine Learning Basics" [2m 15s]
✓ Video 2/47: "Python Tips" [5m 32s]
✗ Video 3/47: "Private Video" (skipped: private)
✓ Video 4/47: "Data Science" [8m 12s]
```

**Log File** (`logs/videodistiller.log`):
```
2025-11-20 10:15:23 INFO     Processing video abc123
2025-11-20 10:15:24 DEBUG    YouTube API response: 200 OK
2025-11-20 10:15:25 WARNING  Video xyz789 is private, skipping
2025-11-20 10:15:26 ERROR    Failed to fetch transcript for def456: TranscriptNotAvailable
```

## Configuration

### Environment Variables (`.env`)

```env
# YouTube Data API
YOUTUBE_API_KEY=AIzaSy...

# LLM Providers (Phase 2)
LLM_PROVIDER=openrouter              # or 'claude'
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...

# Model Selection (Phase 2)
SUMMARIZATION_MODEL=deepseek/deepseek-chat  # Cheap for bulk
ANALYSIS_MODEL=anthropic/claude-sonnet-4.5  # Powerful for quality

# Storage
DATA_DIR=./data
LOG_DIR=./logs
LOG_LEVEL=INFO

# Rate Limits
YOUTUBE_REQUESTS_PER_SECOND=10
LLM_MAX_REQUESTS_PER_MINUTE=60
```

### Validation

**`validate_setup.py`**:
```python
def validate_setup():
    """Check that all required configuration is present."""
    checks = [
        check_youtube_api_key(),
        check_data_directory_writable(),
        check_dependencies_installed(),
    ]

    if all(checks):
        print("✓ Setup validated successfully!")
    else:
        print("✗ Setup validation failed. See errors above.")
        sys.exit(1)
```

## Testing Strategy

### Unit Tests (90% coverage target)

**Data Models**:
```python
def test_video_metadata_serialization():
    video = VideoMetadata(
        id="abc",
        title="Test Video",
        channel="Test Channel",
        ...
    )
    json_data = video.to_dict()
    restored = VideoMetadata.from_dict(json_data)
    assert restored == video
```

**YouTube Extractor** (mocked):
```python
@patch('googleapiclient.discovery.build')
def test_get_video_metadata(mock_youtube):
    mock_youtube.return_value.videos().list().execute.return_value = {
        'items': [{'id': 'abc', 'snippet': {...}}]
    }

    extractor = YouTubeExtractor(api_key="test")
    metadata = extractor.get_metadata("abc")

    assert metadata.title == "Expected Title"
```

### Integration Tests

**Pipeline with Mock Providers**:
```python
def test_pipeline_extract_and_store():
    # Use in-memory implementations
    mock_extractor = MockYouTubeExtractor()
    mock_repo = InMemoryRepository()

    pipeline = Pipeline(mock_extractor, None, None, mock_repo)
    result = pipeline.process_video("test_url")

    # Verify video was stored
    videos = mock_repo.list_all()
    assert len(videos) == 1
    assert videos[0].id == "test_id"
```

### Test Organization

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_youtube_extractor.py
│   ├── test_json_repository.py
│   └── test_pipeline.py
├── integration/
│   ├── test_full_pipeline.py
│   └── test_cli.py
└── fixtures/
    ├── sample_video_metadata.json
    └── sample_transcript.json
```

## Future Phases

### Phase 2: LLM Analysis (Weeks 3-6)

**Features**:
- Multi-level summarization (quick, detailed, chapter-by-chapter)
- Principle extraction from technical content
- Topic tagging and categorization
- Cost tracking per video/provider

**New Components**:
- `ClaudeProvider` implementation
- `OpenRouterProvider` implementation
- `TransformStage` for transcript cleaning
- `AnalyzeStage` for LLM processing

**Configuration**:
- Provider selection and fallback logic
- Cost-based model routing
- Caching of LLM responses

### Phase 3: Search & Query (Weeks 7-10)

**Features**:
- Full-text search in transcripts
- Semantic search with vector embeddings
- Natural language queries
- Topic clustering and recommendations

**New Components**:
- `SQLiteRepository` with FTS5
- Vector embedding generation
- Query interface (CLI and/or API)

### Phase 4: Automation (Weeks 11-14)

**Features**:
- Background monitoring of channels
- Automatic processing of new videos
- Scheduled batch updates
- Webhook support for triggers

**New Components**:
- Scheduler (APScheduler or similar)
- Background worker
- State management for tracking processed videos

## Technology Stack

### Core Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.10"
click = "^8.1.0"              # CLI framework
pydantic = "^2.0"             # Data validation
python-dotenv = "^1.0"        # Environment config
google-api-python-client = "^2.100"  # YouTube API
youtube-transcript-api = "^0.6"      # Transcript fetching
rich = "^13.0"                # Beautiful CLI output

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
pytest-cov = "^4.1"
pytest-mock = "^3.12"
black = "^23.10"
ruff = "^0.1"
mypy = "^1.6"
```

### Future Dependencies (Phase 2)

```toml
anthropic = "^0.7"            # Claude API SDK
openai = "^1.3"               # OpenRouter compatibility
sqlalchemy = "^2.0"           # Database ORM
```

## Success Criteria

### Phase 1 MVP

✅ **Functional**:
- Extract metadata from YouTube video URLs
- Download transcripts (auto-generated or manual)
- Process entire playlists (10+ videos)
- Process channel videos with limit
- Store data as organized JSON files

✅ **Quality**:
- Handles private videos gracefully (skip, don't crash)
- Handles missing transcripts (save metadata only)
- Respects YouTube API rate limits
- Provides clear error messages
- 70%+ test coverage

✅ **Usability**:
- CLI with intuitive commands
- Progress feedback for bulk operations
- Setup validation tool
- Clear documentation (README, QUICKSTART)

✅ **Performance**:
- Process 100 videos in < 10 minutes (API dependent)
- Minimal memory footprint (< 100MB for CLI)
- No data loss on errors

## Migration Path

### JSON → SQLite Migration

**Phase 2 Storage Migration**:
```python
class MigrationTool:
    def migrate_json_to_sqlite(json_dir: str, db_path: str):
        """Migrate existing JSON data to SQLite."""
        repo = JSONRepository(json_dir)
        db = SQLiteRepository(db_path)

        for video in repo.list_all():
            db.save(video)
```

**Advantages**:
- Maintains backward compatibility (can still read JSON)
- Zero data loss
- Enables advanced queries without breaking existing workflows

## Conclusion

This design provides:
- **Clean separation** between interface, business logic, and providers
- **Easy extensibility** via plugin system
- **Low upfront complexity** with clear growth path
- **Cost optimization** through multi-LLM support
- **Robustness** through comprehensive error handling

The modular architecture allows incremental development:
1. Start simple (Phase 1: Extract + Store)
2. Add intelligence (Phase 2: LLM analysis)
3. Scale up (Phase 3: Search and automation)

Each phase builds on the previous without major refactoring.
