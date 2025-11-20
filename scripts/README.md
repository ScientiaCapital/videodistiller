# VideoDistiller Scripts

Automation scripts for School of Knowledge Capital.

## 📺 Watch Later Automation

Extract and catalog all your YouTube Watch Later videos.

### Quick Start

```bash
# Extract + Summarize all Watch Later videos
./scripts/sync_watch_later.sh

# Or use the Python script directly:
python3 scripts/watch_later.py --extract --summarize
```

### Usage Options

```bash
# Extract only (no AI summaries)
python3 scripts/watch_later.py --extract

# Summarize only (must extract first)
python3 scripts/watch_later.py --summarize

# Extract + Summarize + Show summaries
python3 scripts/watch_later.py --extract --summarize --show

# Force a specific template
python3 scripts/watch_later.py --extract --summarize --template history
```

### Automation with Cron

Run daily at 2 AM to sync Watch Later:

```bash
# Edit crontab
crontab -e

# Add this line (replace PATH with your project path):
0 2 * * * cd /Users/tmkipper/Desktop/tk_projects/videodistiller && ./scripts/sync_watch_later.sh >> logs/cron.log 2>&1
```

## 📚 Subscriptions Sync

Extract latest videos from your favorite channels.

See `subscriptions.py` for channel management.

## 📊 Output Locations

- **Metadata**: `data/metadata/*.json` - Video information
- **Transcripts**: `data/transcripts/*.txt` - Full text transcripts
- **Summaries**: `data/summaries/*.json` - Kid-friendly summaries
- **Costs**: `data/llm_costs.json` - Budget tracking

## 💰 Budget Management

Default budget: $10/month with $8 warning threshold.

Configure in `.env`:
```
MAX_MONTHLY_COST=10.00
WARN_AT_COST=8.00
```

Check current spending:
```bash
cat data/llm_costs.json
```

## 🔧 Troubleshooting

**No videos extracted?**
- Check your `YOUTUBE_API_KEY` in `.env`
- Verify Watch Later playlist is not empty
- Check logs in `logs/` directory

**Summarization fails?**
- Check your `OPENROUTER_API_KEY` in `.env`
- Verify budget not exceeded: `cat data/llm_costs.json`
- Run with `--extract` first to get transcripts

**API quota exceeded?**
- YouTube API has daily quotas
- Try again tomorrow or use a different API key
