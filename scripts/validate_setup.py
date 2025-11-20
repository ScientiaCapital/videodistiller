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


def check_api_key_works():
    """Test the API key by making a test request."""
    from dotenv import load_dotenv
    import os

    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')

    if not api_key or api_key == 'your_youtube_api_key_here':
        # Already reported in check_api_key
        return False

    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError

        # Make a minimal test request
        youtube = build('youtube', 'v3', developerKey=api_key)
        # Search for a single video to test the API key
        youtube.videos().list(part='id', id='dQw4w9WgXcQ', maxResults=1).execute()

        print("✓ YouTube API key is valid and working")
        return True
    except HttpError as e:
        if e.resp.status == 403:
            print("✗ YouTube API key is invalid or quota exceeded")
            print("  Check your API key in Google Cloud Console")
        else:
            print(f"✗ YouTube API error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing API key: {e}")
        return False


def check_directories():
    """Check data directories can be created."""
    try:
        # Add parent directory to path so we can import src
        import sys
        from pathlib import Path
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))

        from src.utils.config import Config

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
        check_api_key_works(),
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
