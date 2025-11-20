"""Tests for logging setup."""
import logging
import re
from pathlib import Path
from unittest.mock import Mock
from src.utils.logging import setup_logging
from src.utils.config import Config


def test_setup_logging_creates_logger(tmp_path, monkeypatch):
    """Test setup_logging creates configured logger."""
    # Mock config
    config = Mock(spec=Config)
    config.log_level = "DEBUG"
    config.log_dir = tmp_path

    logger = setup_logging(config)

    assert logger.name == "videodistiller"
    assert logger.level == logging.DEBUG


def test_setup_logging_writes_to_file(tmp_path, monkeypatch):
    """Test setup_logging writes messages to file."""
    # Mock config
    config = Mock(spec=Config)
    config.log_level = "INFO"
    config.log_dir = tmp_path

    logger = setup_logging(config)
    logger.info("Test message")

    # Find the log file with timestamp pattern
    log_files = list(tmp_path.glob("videodistiller_*.log"))
    assert len(log_files) == 1
    assert "Test message" in log_files[0].read_text()


def test_setup_logging_timestamp_in_filename(tmp_path):
    """Test setup_logging creates log file with timestamp."""
    # Mock config
    config = Mock(spec=Config)
    config.log_level = "INFO"
    config.log_dir = tmp_path

    logger = setup_logging(config)

    # Check that log file has timestamp pattern
    log_files = list(tmp_path.glob("videodistiller_*.log"))
    assert len(log_files) == 1

    # Verify filename matches pattern: videodistiller_YYYYMMDD_HHMMSS.log
    pattern = r"videodistiller_\d{8}_\d{6}\.log"
    assert re.match(pattern, log_files[0].name)


def test_setup_logging_uses_rich_handler(tmp_path):
    """Test setup_logging uses RichHandler for console output."""
    from rich.logging import RichHandler

    # Mock config
    config = Mock(spec=Config)
    config.log_level = "INFO"
    config.log_dir = tmp_path

    logger = setup_logging(config)

    # Check that console handler is RichHandler
    console_handlers = [h for h in logger.handlers if isinstance(h, RichHandler)]
    assert len(console_handlers) == 1
    assert console_handlers[0].level == logging.INFO


def test_setup_logging_respects_log_level(tmp_path):
    """Test console handler respects log level from config."""
    # Mock config
    config = Mock(spec=Config)
    config.log_level = "WARNING"
    config.log_dir = tmp_path

    logger = setup_logging(config)

    # Check that logger and console handler use correct level
    assert logger.level == logging.WARNING

    from rich.logging import RichHandler
    console_handlers = [h for h in logger.handlers if isinstance(h, RichHandler)]
    assert len(console_handlers) == 1
    assert console_handlers[0].level == logging.WARNING
