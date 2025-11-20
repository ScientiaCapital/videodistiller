# VideoDistiller - Quick Start Guide

Get VideoDistiller running in 10 minutes.

## Step 1: Prerequisites

- Python 3.10 or higher
- pip package manager
- YouTube Data API v3 key

## Step 2: Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "YouTube Data API v3"
4. Create credentials → API Key
5. Copy the API key

## Step 3: Install

```bash
# Clone or navigate to project
cd videodistiller

# Install dependencies
pip install -r requirements.txt

# Or use pip install -e . for development
pip install -e ".[dev]"
```

## Step 4: Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# YOUTUBE_API_KEY=your_key_here
```

## Step 5: Validate

```bash
python validate_setup.py
```

Expected output:
```
✓ YouTube API key configured
✓ Data directory writable
✓ Dependencies installed
✓ Setup validated successfully!
```

## Step 6: Extract Your First Video

```bash
# Single video
videodistiller extract --url "https://youtube.com/watch?v=dQw4w9WgXcQ"

# Playlist
videodistiller extract --playlist "https://youtube.com/playlist?list=PLxxx"

# Channel (recent 10 videos)
videodistiller extract --channel "UCxxx" --limit 10
```

## What Gets Created

```
data/
├── metadata/
│   ├── videos.json           # Index of all videos
│   └── VIDEO_ID.json         # Individual video metadata
└── transcripts/
    └── VIDEO_ID.txt          # Raw transcript text

logs/
└── videodistiller.log        # Application logs
```

## Troubleshooting

**"Quota exceeded" error:**
- YouTube API has daily quota limits
- Wait 24 hours or increase quota in Google Cloud Console

**"No transcript available" warning:**
- Some videos don't have transcripts
- VideoDistiller will save metadata only

**"Private video" warning:**
- Private videos are skipped automatically
- This is expected behavior
