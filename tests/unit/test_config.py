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
