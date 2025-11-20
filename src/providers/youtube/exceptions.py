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
