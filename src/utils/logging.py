"""Logging configuration for VideoDistiller."""
import logging
from datetime import datetime
from pathlib import Path

from rich.logging import RichHandler

from src.utils.config import Config


def setup_logging(config: Config) -> logging.Logger:
    """
    Configure application logging with Rich console output.

    Args:
        config: Application configuration object

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("videodistiller")
    logger.setLevel(getattr(logging, config.log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with Rich (user-friendly)
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=False  # Timestamp already in file handler
    )
    console_handler.setLevel(getattr(logging, config.log_level.upper()))
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console_handler)

    # File handler (detailed) with timestamp in filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = config.log_dir / f"videodistiller_{timestamp}.log"
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
