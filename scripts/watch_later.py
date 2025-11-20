#!/usr/bin/env python3
"""
Watch Later Automation Script

Automatically extract and catalog all videos from your YouTube Watch Later playlist.
Can also auto-summarize videos for School of Knowledge Capital.

Usage:
    python3 scripts/watch_later.py --extract                    # Extract only
    python3 scripts/watch_later.py --extract --summarize        # Extract + summarize
    python3 scripts/watch_later.py --summarize                  # Summarize existing
    python3 scripts/watch_later.py --extract --summarize --show # Show summaries
"""

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


def print_banner():
    """Print welcome banner."""
    click.echo("=" * 70)
    click.echo("  📺 Watch Later Automation - School of Knowledge Capital")
    click.echo("=" * 70)
    click.echo()


def print_stats(stats: dict):
    """Print statistics."""
    click.echo("\n" + "=" * 70)
    click.echo("  📊 Statistics")
    click.echo("=" * 70)
    for key, value in stats.items():
        click.echo(f"  {key}: {value}")
    click.echo()


@click.command()
@click.option('--extract', is_flag=True, help='Extract videos from Watch Later')
@click.option('--summarize', is_flag=True, help='Summarize extracted videos')
@click.option('--show', is_flag=True, help='Show generated summaries')
@click.option('--template', type=click.Choice([
    'general', 'tech_ai', 'finance', 'history', 'geography',
    'art', 'science', 'stem', 'programming'
]), help='Force specific template (default: auto-detect)')
def main(extract, summarize, show, template):
    """Watch Later automation script for School of Knowledge Capital."""

    if not extract and not summarize:
        click.echo("Error: Specify --extract and/or --summarize", err=True)
        click.echo("Run 'python3 scripts/watch_later.py --help' for usage", err=True)
        sys.exit(1)

    print_banner()

    # Load configuration
    config = Config()
    config.ensure_directories_exist()
    logger = setup_logging(config)

    stats = {
        "Start Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Videos Extracted": 0,
        "Videos Summarized": 0,
        "Total Cost": "$0.00",
        "Errors": 0
    }

    # PHASE 1: EXTRACTION
    if extract:
        click.echo("🎬 Phase 1: Extracting Watch Later Videos")
        click.echo("-" * 70)

        if not config.youtube_api_key:
            click.echo("❌ Error: YOUTUBE_API_KEY not configured in .env", err=True)
            sys.exit(1)

        try:
            # Initialize extraction components
            extractor = YouTubeExtractor(api_key=config.youtube_api_key)
            repository = JSONRepository(data_dir=config.data_dir)
            pipeline = Pipeline(extractor=extractor, repository=repository)

            click.echo("📋 Fetching Watch Later playlist (ID: WL)...")
            start_time = time.time()

            # Extract all Watch Later videos
            results = pipeline.process_playlist("WL")

            elapsed = time.time() - start_time
            stats["Videos Extracted"] = len(results)

            click.echo(f"\n✅ Extracted {len(results)} videos in {elapsed:.1f} seconds")

            # Show sample of extracted videos
            if results:
                click.echo("\n📝 Sample of extracted videos:")
                for i, video in enumerate(results[:5], 1):
                    click.echo(f"  {i}. {video.title}")
                    click.echo(f"     Channel: {video.channel_title}")
                    click.echo(f"     Duration: {video.duration}s")
                    if video.transcript:
                        click.echo(f"     Transcript: {len(video.transcript.text)} chars")
                    click.echo()

                if len(results) > 5:
                    click.echo(f"  ... and {len(results) - 5} more videos")

        except KeyboardInterrupt:
            click.echo("\n\n⚠️  Extraction interrupted by user")
            stats["Errors"] += 1
        except Exception as e:
            click.echo(f"\n❌ Extraction failed: {e}", err=True)
            logger.exception("Watch Later extraction failed")
            stats["Errors"] += 1
            if not summarize:
                print_stats(stats)
                sys.exit(1)

    # PHASE 2: SUMMARIZATION
    if summarize:
        click.echo("\n" + "=" * 70)
        click.echo("🤖 Phase 2: Generating Kid-Friendly Summaries")
        click.echo("-" * 70)

        if not config.openrouter_api_key:
            click.echo("❌ Error: OPENROUTER_API_KEY not configured in .env", err=True)
            click.echo("Skipping summarization...")
            print_stats(stats)
            sys.exit(1)

        try:
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

            # Get all video IDs
            metadata_dir = config.data_dir / "metadata"
            video_ids = [f.stem for f in metadata_dir.glob("*.json")]

            if not video_ids:
                click.echo("⚠️  No videos found. Run with --extract first.")
                print_stats(stats)
                sys.exit(0)

            # Show budget status
            usage = cost_tracker.get_usage_summary()
            click.echo(f"\n💰 Budget Status:")
            click.echo(f"   Used: ${usage['total_cost']:.2f} / ${cost_tracker.max_monthly_cost:.2f}")
            click.echo(f"   Remaining: ${usage['remaining_budget']:.2f}")
            click.echo(f"   ({usage['budget_used_percent']:.1f}% used)\n")

            click.echo(f"📚 Processing {len(video_ids)} videos...")
            if template:
                click.echo(f"   Template: {template} (forced)")
            else:
                click.echo(f"   Template: auto-detect")
            click.echo()

            start_time = time.time()

            # Summarize all videos
            summaries = analyzer.summarize_batch(
                video_ids=video_ids,
                template_name=template,
                auto_detect=(template is None),
                skip_existing=True
            )

            elapsed = time.time() - start_time
            stats["Videos Summarized"] = len(summaries)

            # Update cost stats
            usage = cost_tracker.get_usage_summary()
            stats["Total Cost"] = f"${usage['total_cost']:.2f}"

            click.echo(f"\n✅ Generated {len(summaries)} summaries in {elapsed:.1f} seconds")

            # Show template distribution
            if summaries:
                template_counts = {}
                for summary in summaries:
                    template_counts[summary.template_used] = template_counts.get(summary.template_used, 0) + 1

                click.echo("\n📊 Templates Used:")
                for tmpl, count in sorted(template_counts.items(), key=lambda x: -x[1]):
                    click.echo(f"   {tmpl}: {count} videos")

                # Show summaries if requested
                if show:
                    click.echo("\n" + "=" * 70)
                    click.echo("📖 Generated Summaries")
                    click.echo("=" * 70)

                    for i, summary in enumerate(summaries, 1):
                        click.echo(f"\n[{i}/{len(summaries)}] {summary.title}")
                        click.echo(f"Template: {summary.template_used} | Tokens: {summary.tokens_used} | Cost: ${summary.cost:.4f}")
                        click.echo("-" * 70)
                        click.echo(summary.summary_text)
                        click.echo("=" * 70)

            # Final budget status
            click.echo(f"\n💰 Final Budget:")
            click.echo(f"   Total Spent: ${usage['total_cost']:.2f}")
            click.echo(f"   Remaining: ${usage['remaining_budget']:.2f}")
            click.echo(f"   Budget Used: {usage['budget_used_percent']:.1f}%")

        except KeyboardInterrupt:
            click.echo("\n\n⚠️  Summarization interrupted by user")
            stats["Errors"] += 1
        except Exception as e:
            click.echo(f"\n❌ Summarization failed: {e}", err=True)
            logger.exception("Summarization failed")
            stats["Errors"] += 1

    # Final stats
    stats["End Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print_stats(stats)

    if stats["Errors"] > 0:
        click.echo("⚠️  Completed with errors. Check logs for details.")
        sys.exit(1)
    else:
        click.echo("🎉 All done! Your Watch Later videos are catalogued.")
        click.echo()
        click.echo("📁 Files saved to:")
        click.echo(f"   Metadata: {config.data_dir / 'metadata'}")
        click.echo(f"   Transcripts: {config.data_dir / 'transcripts'}")
        click.echo(f"   Summaries: {config.data_dir / 'summaries'}")
        click.echo()


if __name__ == '__main__':
    main()
