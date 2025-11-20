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
