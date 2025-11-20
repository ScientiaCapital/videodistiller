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
    logger = setup_logging(config)

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
