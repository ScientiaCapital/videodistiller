# VideoDistiller

A powerful pipeline for extracting, processing, and analyzing video content from YouTube.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure YouTube API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your YOUTUBE_API_KEY
   ```

3. Validate setup:
   ```bash
   python validate_setup.py
   ```

4. Extract a video:
   ```bash
   videodistiller extract --url "https://youtube.com/watch?v=..."
   ```

## Features

- Extract video metadata from YouTube URLs
- Download transcripts (auto-generated or manual)
- Process entire playlists and channels
- Store data in organized JSON format

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## Project Structure

```
videodistiller/
├── src/              # Source code
├── tests/            # Tests
├── data/             # Extracted data (created at runtime)
├── logs/             # Application logs (created at runtime)
└── docs/             # Documentation
```
