"""Tests for content analyzer."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.core.models import VideoMetadata
from src.llm.analyzer import ContentAnalyzer, Summary
from src.llm.openrouter_client import UsageMetrics


class TestSummary:
    """Test Summary dataclass."""

    def test_summary_creation(self):
        """Test creating a summary."""
        summary = Summary(
            video_id="test123",
            title="Test Video",
            channel_title="Test Channel",
            summary_text="This is a test summary.",
            template_used="general",
            tokens_used=150,
            cost=0.0525,
            created_at=datetime.now()
        )

        assert summary.video_id == "test123"
        assert summary.title == "Test Video"
        assert summary.channel_title == "Test Channel"
        assert summary.summary_text == "This is a test summary."
        assert summary.template_used == "general"
        assert summary.tokens_used == 150
        assert summary.cost == 0.0525

    def test_summary_to_dict(self):
        """Test converting summary to dictionary."""
        summary = Summary(
            video_id="test123",
            title="Test Video",
            channel_title="Test Channel",
            summary_text="Test summary",
            template_used="general",
            tokens_used=150,
            cost=0.0525,
            created_at=datetime.now(),
            reading_level="Grade 5-6"
        )

        data = summary.to_dict()

        assert data["video_id"] == "test123"
        assert data["title"] == "Test Video"
        assert data["reading_level"] == "Grade 5-6"

    def test_summary_from_dict(self):
        """Test creating summary from dictionary."""
        data = {
            "video_id": "test123",
            "title": "Test Video",
            "channel_title": "Test Channel",
            "summary_text": "Test summary",
            "template_used": "general",
            "tokens_used": 150,
            "cost": 0.0525,
            "created_at": "2024-11-20T10:00:00",
            "reading_level": "Grade 5-6"
        }

        summary = Summary.from_dict(data)

        assert summary.video_id == "test123"
        assert summary.reading_level == "Grade 5-6"


class TestContentAnalyzer:
    """Test ContentAnalyzer."""

    def setup_test_data(self, tmpdir: Path) -> None:
        """Set up test video data in temporary directory."""
        # Create directories
        metadata_dir = tmpdir / "metadata"
        transcript_dir = tmpdir / "transcripts"
        metadata_dir.mkdir(parents=True)
        transcript_dir.mkdir(parents=True)

        # Create test metadata
        metadata = {
            "id": "test123",
            "title": "How Plants Grow",
            "channel_title": "Science for Kids",
            "channel_id": "UC123456",
            "duration": 300,
            "published_at": "2024-01-15T10:00:00",
            "description": "Learn how plants grow in this educational video.",
            "tags": ["science", "education", "plants"],
            "view_count": 1000,
            "like_count": 50,
            "comment_count": 10,
            "thumbnail_url": "https://example.com/thumb.jpg",
            "extracted_at": "2024-11-20T10:00:00"
        }

        with open(metadata_dir / "test123.json", 'w') as f:
            json.dump(metadata, f)

        # Create test transcript
        transcript = "Plants need water and sunlight to grow. They use photosynthesis to make food."

        with open(transcript_dir / "test123.txt", 'w') as f:
            f.write(transcript)

    def test_analyzer_initialization(self):
        """Test initializing analyzer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_client = Mock()
            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=Path(tmpdir)
            )

            assert analyzer.llm_client == mock_client
            assert analyzer.summary_dir.exists()

    def test_load_metadata(self):
        """Test loading video metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            self.setup_test_data(tmpdir)

            mock_client = Mock()
            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=tmpdir
            )

            metadata = analyzer._load_metadata("test123")

            assert metadata.id == "test123"
            assert metadata.title == "How Plants Grow"
            assert metadata.channel_title == "Science for Kids"

    def test_load_metadata_not_found(self):
        """Test error when metadata not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_client = Mock()
            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=Path(tmpdir)
            )

            with pytest.raises(FileNotFoundError):
                analyzer._load_metadata("nonexistent")

    def test_load_transcript(self):
        """Test loading video transcript."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            self.setup_test_data(tmpdir)

            mock_client = Mock()
            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=tmpdir
            )

            transcript = analyzer._load_transcript("test123")

            assert "Plants need water" in transcript
            assert "photosynthesis" in transcript

    def test_load_transcript_not_found(self):
        """Test error when transcript not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_client = Mock()
            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=Path(tmpdir)
            )

            with pytest.raises(FileNotFoundError):
                analyzer._load_transcript("nonexistent")

    def test_summarize_video(self):
        """Test summarizing a video."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            self.setup_test_data(tmpdir)

            # Mock LLM client
            mock_client = Mock()
            mock_metrics = UsageMetrics(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                cost=0.0525,
                model="qwen/qwen-2.5-72b-instruct"
            )
            mock_client.complete.return_value = (
                "This is a kid-friendly summary about plants.",
                mock_metrics
            )

            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=tmpdir
            )

            summary = analyzer.summarize_video("test123")

            assert summary.video_id == "test123"
            assert summary.title == "How Plants Grow"
            assert summary.summary_text == "This is a kid-friendly summary about plants."
            assert summary.tokens_used == 150
            assert summary.cost == 0.0525

            # Verify summary was saved
            summary_file = tmpdir / "summaries" / "test123.json"
            assert summary_file.exists()

    def test_summarize_video_with_template(self):
        """Test summarizing with specific template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            self.setup_test_data(tmpdir)

            mock_client = Mock()
            mock_metrics = UsageMetrics(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                cost=0.0525,
                model="qwen/qwen-2.5-72b-instruct"
            )
            mock_client.complete.return_value = (
                "Summary text",
                mock_metrics
            )

            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=tmpdir
            )

            summary = analyzer.summarize_video(
                "test123",
                template_name="general"
            )

            assert summary.template_used == "general"

    @patch('src.llm.analyzer.auto_detect_template')
    def test_summarize_video_auto_detect(self, mock_auto_detect):
        """Test summarizing with auto-detected template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            self.setup_test_data(tmpdir)

            mock_auto_detect.return_value = "tech_ai"

            mock_client = Mock()
            mock_metrics = UsageMetrics(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                cost=0.0525,
                model="qwen/qwen-2.5-72b-instruct"
            )
            mock_client.complete.return_value = (
                "Summary text",
                mock_metrics
            )

            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=tmpdir
            )

            summary = analyzer.summarize_video(
                "test123",
                auto_detect=True
            )

            assert summary.template_used == "tech_ai"
            assert mock_auto_detect.called

    def test_get_summary(self):
        """Test retrieving existing summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            self.setup_test_data(tmpdir)

            mock_client = Mock()
            mock_metrics = UsageMetrics(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                cost=0.0525,
                model="qwen/qwen-2.5-72b-instruct"
            )
            mock_client.complete.return_value = (
                "Summary text",
                mock_metrics
            )

            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=tmpdir
            )

            # Create summary
            analyzer.summarize_video("test123")

            # Retrieve summary
            summary = analyzer.get_summary("test123")

            assert summary is not None
            assert summary.video_id == "test123"

    def test_get_summary_not_found(self):
        """Test getting summary that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_client = Mock()
            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=Path(tmpdir)
            )

            summary = analyzer.get_summary("nonexistent")

            assert summary is None

    def test_list_summaries(self):
        """Test listing all summaries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            self.setup_test_data(tmpdir)

            mock_client = Mock()
            mock_metrics = UsageMetrics(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                cost=0.0525,
                model="qwen/qwen-2.5-72b-instruct"
            )
            mock_client.complete.return_value = (
                "Summary text",
                mock_metrics
            )

            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=tmpdir
            )

            # Create summary
            analyzer.summarize_video("test123")

            # List summaries
            summaries = analyzer.list_summaries()

            assert "test123" in summaries
            assert len(summaries) == 1

    def test_summarize_batch(self):
        """Test batch summarization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            self.setup_test_data(tmpdir)

            mock_client = Mock()
            mock_metrics = UsageMetrics(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                cost=0.0525,
                model="qwen/qwen-2.5-72b-instruct"
            )
            mock_client.complete.return_value = (
                "Summary text",
                mock_metrics
            )

            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=tmpdir
            )

            summaries = analyzer.summarize_batch(["test123"])

            assert len(summaries) == 1
            assert summaries[0].video_id == "test123"

    def test_summarize_batch_skip_existing(self):
        """Test batch skipping existing summaries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            self.setup_test_data(tmpdir)

            mock_client = Mock()
            mock_metrics = UsageMetrics(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                cost=0.0525,
                model="qwen/qwen-2.5-72b-instruct"
            )
            mock_client.complete.return_value = (
                "Summary text",
                mock_metrics
            )

            analyzer = ContentAnalyzer(
                llm_client=mock_client,
                data_dir=tmpdir
            )

            # First batch
            analyzer.summarize_batch(["test123"])

            # Second batch with skip_existing
            summaries = analyzer.summarize_batch(
                ["test123"],
                skip_existing=True
            )

            # Should return empty list (skipped existing)
            assert len(summaries) == 0
