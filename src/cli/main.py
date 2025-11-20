"""Main CLI application."""
import sys

import click

from src.cli.utils import extract_playlist_id, extract_video_id
from src.llm.analyzer import ContentAnalyzer
from src.llm.openrouter_client import OpenRouterClient, CostTracker
from src.pipeline.pipeline import Pipeline
from src.providers.storage.json_repo import JSONRepository
from src.providers.youtube.extractor import YouTubeExtractor
from src.utils.config import Config
from src.utils.logging import setup_logging


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
            click.echo(f"  Channel: {result.channel_title}")
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
@click.argument('video_ids', nargs=-1, required=True)
@click.option('--template', type=click.Choice(['general', 'tech_ai', 'finance']), help='Template to use (default: auto-detect)')
@click.option('--all', 'all_videos', is_flag=True, help='Summarize all extracted videos')
@click.option('--skip-existing', is_flag=True, default=True, help='Skip videos with existing summaries')
@click.option('--show', is_flag=True, help='Show generated summary')
def summarize(video_ids, template, all_videos, skip_existing, show):
    """Generate kid-friendly summaries for videos.

    Examples:
        videodistiller summarize VIDEO_ID
        videodistiller summarize VIDEO_ID1 VIDEO_ID2 VIDEO_ID3
        videodistiller summarize --all
        videodistiller summarize --template tech_ai VIDEO_ID
    """
    # Load configuration
    config = Config()

    # Setup logging
    logger = setup_logging(config)

    # Check OpenRouter API key
    if not config.openrouter_api_key:
        click.echo("Error: OPENROUTER_API_KEY not configured in .env", err=True)
        click.echo("See docs/plans/2025-11-20-phase2-llm-summarization-design.md", err=True)
        sys.exit(1)

    # Initialize LLM components
    cost_tracker = CostTracker(
        data_dir=config.data_dir,
        max_monthly_cost=config.max_monthly_cost,
        warn_at_cost=config.warn_at_cost
    )

    llm_client = OpenRouterClient(
        api_key=config.openrouter_api_key,
        model=config.llm_model,
        cost_tracker=cost_tracker
    )

    analyzer = ContentAnalyzer(
        llm_client=llm_client,
        data_dir=config.data_dir,
        cost_tracker=cost_tracker
    )

    try:
        # Determine which videos to summarize
        if all_videos:
            # Get all video IDs from metadata directory
            metadata_dir = config.data_dir / "metadata"
            video_ids = [f.stem for f in metadata_dir.glob("*.json")]
            if not video_ids:
                click.echo("No videos found. Run 'videodistiller extract' first.")
                sys.exit(1)
            click.echo(f"Found {len(video_ids)} videos")

        if not video_ids:
            click.echo("Error: No video IDs specified", err=True)
            click.echo("Run 'videodistiller summarize --help' for usage", err=True)
            sys.exit(1)

        # Show budget status
        usage = cost_tracker.get_usage_summary()
        click.echo(f"\nBudget: ${usage['total_cost']:.2f} / ${cost_tracker.max_monthly_cost:.2f} ({usage['budget_used_percent']:.1f}%)")
        click.echo(f"Remaining: ${usage['remaining_budget']:.2f}\n")

        # Summarize videos
        click.echo(f"Summarizing {len(video_ids)} video(s)...")

        summaries = analyzer.summarize_batch(
            video_ids=list(video_ids),
            template_name=template,
            auto_detect=(template is None),
            skip_existing=skip_existing
        )

        # Display results
        click.echo(f"\n✓ Generated {len(summaries)} summaries")

        for summary in summaries:
            click.echo(f"\n{summary.title}")
            click.echo(f"  Video ID: {summary.video_id}")
            click.echo(f"  Template: {summary.template_used}")
            click.echo(f"  Tokens: {summary.tokens_used}")
            click.echo(f"  Cost: ${summary.cost:.4f}")

            if show:
                click.echo(f"\n{summary.summary_text}\n")
                click.echo("-" * 80)

        # Final budget status
        usage = cost_tracker.get_usage_summary()
        click.echo(f"\nFinal budget: ${usage['total_cost']:.2f} / ${cost_tracker.max_monthly_cost:.2f} ({usage['budget_used_percent']:.1f}%)")

    except KeyboardInterrupt:
        click.echo("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception("Summarization failed")
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
        import googleapiclient  # noqa: F401
        import youtube_transcript_api  # noqa: F401
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
