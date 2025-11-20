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
