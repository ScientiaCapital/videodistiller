#!/usr/bin/env python3
"""
YouTube Subscriptions Manager

Extract latest videos from your favorite YouTube channels.
Manages a list of channels you're interested in for School of Knowledge Capital.

Usage:
    python3 scripts/subscriptions.py --add CHANNEL_ID --name "Channel Name"
    python3 scripts/subscriptions.py --list
    python3 scripts/subscriptions.py --sync
    python3 scripts/subscriptions.py --sync --summarize
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import click

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import Config
from src.utils.logging import setup_logging
from src.pipeline.pipeline import Pipeline
from src.providers.storage.json_repo import JSONRepository
from src.providers.youtube.extractor import YouTubeExtractor
from src.llm.analyzer import ContentAnalyzer
from src.llm.openrouter_client import OpenRouterClient, CostTracker


CHANNELS_FILE = Path(__file__).parent / "favorite_channels.json"


def load_channels():
    """Load favorite channels list."""
    if not CHANNELS_FILE.exists():
        return []

    with open(CHANNELS_FILE, 'r') as f:
        return json.load(f)


def save_channels(channels):
    """Save favorite channels list."""
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(channels, f, indent=2)


@click.group()
def cli():
    """Manage your favorite YouTube channels for School of Knowledge Capital."""
    pass


@cli.command()
@click.option('--channel-id', required=True, help='YouTube channel ID (e.g., UCsXVk37bltHxD1rDPwtNM8Q)')
@click.option('--name', required=True, help='Channel name (e.g., "Kurzgesagt")')
@click.option('--category', help='Category (e.g., science, history, tech)')
@click.option('--limit', type=int, default=20, help='Number of videos to fetch per sync')
def add(channel_id, name, category, limit):
    """Add a channel to your favorites."""
    channels = load_channels()

    # Check if already exists
    for ch in channels:
        if ch['channel_id'] == channel_id:
            click.echo(f"⚠️  Channel {name} already in favorites")
            return

    channel = {
        'channel_id': channel_id,
        'name': name,
        'category': category or 'general',
        'limit': limit,
        'added_at': datetime.now().isoformat()
    }

    channels.append(channel)
    save_channels(channels)

    click.echo(f"✅ Added {name} to favorites")
    click.echo(f"   Channel ID: {channel_id}")
    click.echo(f"   Category: {channel['category']}")
    click.echo(f"   Videos per sync: {limit}")


@cli.command()
@click.option('--channel-id', required=True, help='YouTube channel ID to remove')
def remove(channel_id):
    """Remove a channel from favorites."""
    channels = load_channels()
    original_count = len(channels)

    channels = [ch for ch in channels if ch['channel_id'] != channel_id]

    if len(channels) < original_count:
        save_channels(channels)
        click.echo(f"✅ Removed channel {channel_id}")
    else:
        click.echo(f"⚠️  Channel {channel_id} not found in favorites")


@cli.command()
def list():
    """List all favorite channels."""
    channels = load_channels()

    if not channels:
        click.echo("📝 No favorite channels yet.")
        click.echo("\nAdd channels with:")
        click.echo("  python3 scripts/subscriptions.py add --channel-id UC... --name 'Channel Name'")
        return

    click.echo(f"\n📺 Favorite Channels ({len(channels)} total)")
    click.echo("=" * 70)

    # Group by category
    by_category = {}
    for ch in channels:
        cat = ch.get('category', 'general')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(ch)

    for category, chans in sorted(by_category.items()):
        click.echo(f"\n{category.upper()}:")
        for ch in chans:
            click.echo(f"  • {ch['name']}")
            click.echo(f"    ID: {ch['channel_id']}")
            click.echo(f"    Videos/sync: {ch.get('limit', 20)}")

    click.echo()


@cli.command()
@click.option('--summarize', is_flag=True, help='Also generate summaries')
@click.option('--template', help='Force specific template')
def sync(summarize, template):
    """Sync latest videos from all favorite channels."""
    channels = load_channels()

    if not channels:
        click.echo("⚠️  No favorite channels configured.")
        click.echo("Add channels first with: python3 scripts/subscriptions.py add")
        return

    click.echo("=" * 70)
    click.echo(f"  📺 Syncing {len(channels)} Favorite Channels")
    click.echo("=" * 70)
    click.echo()

    # Load configuration
    config = Config()
    config.ensure_directories_exist()
    logger = setup_logging(config)

    if not config.youtube_api_key:
        click.echo("❌ Error: YOUTUBE_API_KEY not configured in .env", err=True)
        sys.exit(1)

    # Initialize extraction
    extractor = YouTubeExtractor(api_key=config.youtube_api_key)
    repository = JSONRepository(data_dir=config.data_dir)
    pipeline = Pipeline(extractor=extractor, repository=repository)

    total_extracted = 0
    errors = 0

    # Extract from each channel
    for i, channel in enumerate(channels, 1):
        try:
            click.echo(f"[{i}/{len(channels)}] {channel['name']}")
            click.echo(f"  Fetching latest {channel.get('limit', 20)} videos...")

            start = time.time()
            results = pipeline.process_channel(
                channel['channel_id'],
                limit=channel.get('limit', 20)
            )
            elapsed = time.time() - start

            click.echo(f"  ✅ Extracted {len(results)} videos in {elapsed:.1f}s")
            total_extracted += len(results)

        except Exception as e:
            click.echo(f"  ❌ Error: {e}")
            errors += 1

        click.echo()

    click.echo("=" * 70)
    click.echo(f"✅ Extraction complete:")
    click.echo(f"   Total videos: {total_extracted}")
    click.echo(f"   Errors: {errors}")
    click.echo("=" * 70)

    # Summarization phase
    if summarize:
        click.echo()
        click.echo("🤖 Phase 2: Generating Summaries")
        click.echo("=" * 70)

        if not config.openrouter_api_key:
            click.echo("❌ Error: OPENROUTER_API_KEY not configured", err=True)
            return

        try:
            # Initialize LLM
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

            # Get all videos
            metadata_dir = config.data_dir / "metadata"
            video_ids = [f.stem for f in metadata_dir.glob("*.json")]

            # Show budget
            usage = cost_tracker.get_usage_summary()
            click.echo(f"💰 Budget: ${usage['total_cost']:.2f} / ${cost_tracker.max_monthly_cost:.2f}")
            click.echo(f"   Remaining: ${usage['remaining_budget']:.2f}\n")

            # Summarize
            summaries = analyzer.summarize_batch(
                video_ids=video_ids,
                template_name=template,
                auto_detect=(template is None),
                skip_existing=True
            )

            click.echo(f"\n✅ Generated {len(summaries)} summaries")

            # Final budget
            usage = cost_tracker.get_usage_summary()
            click.echo(f"\n💰 Final: ${usage['total_cost']:.2f} ({usage['budget_used_percent']:.1f}% used)")

        except Exception as e:
            click.echo(f"❌ Summarization error: {e}", err=True)


@cli.command()
def popular():
    """Show popular educational channels to add."""
    click.echo("\n📚 Popular Educational Channels")
    click.echo("=" * 70)

    popular_channels = [
        ("Kurzgesagt", "UCsXVk37bltHxD1rDPwtNM8Q", "science"),
        ("Veritasium", "UCHnyfMqiRRG1u-2MsSQLbXA", "science"),
        ("CrashCourse", "UCX6b17PVsYBQ0ip5gyeme-Q", "general"),
        ("Khan Academy", "UCWph-WDYGBdE7jCQSNfBnlg", "stem"),
        ("TED-Ed", "UCsooa4yRKGN_zEE8iknghZA", "general"),
        ("National Geographic", "UCpVm7bg6pXKo1Pr6k5kxG9A", "geography"),
        ("History Matters", "UC22BdTgxefuvUivrjesETjg", "history"),
        ("3Blue1Brown", "UCYO_jab_esuFRV4b17AJtAw", "stem"),
        ("The Coding Train", "UCvjgXvBlbQiydffZU7m1_aw", "programming"),
        ("Art for Kids Hub", "UC5XMF3Inoi8R9nSI8ChOsdQ", "art"),
    ]

    for name, channel_id, category in popular_channels:
        click.echo(f"\n{name} ({category})")
        click.echo(f"  {channel_id}")
        click.echo(f"  Add: python3 scripts/subscriptions.py add --channel-id {channel_id} --name '{name}' --category {category}")

    click.echo()


if __name__ == '__main__':
    cli()
