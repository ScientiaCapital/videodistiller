# Phase 2: LLM Summarization & Knowledge Capital Web Viewer

**Design Date:** 2025-11-20
**Status:** Design Complete - Ready for Implementation
**Purpose:** Create kid-friendly video summaries (Grade 5-6 reading level) and deploy as "School of Knowledge Capital" web app

---

## Table of Contents
1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Architecture](#architecture)
4. [Prompt Templates](#prompt-templates)
5. [OpenRouter Integration](#openrouter-integration)
6. [Error Handling](#error-handling)
7. [Data Flow](#data-flow)
8. [Web Viewer](#web-viewer)
9. [Deployment Strategy](#deployment-strategy)
10. [Implementation Plan](#implementation-plan)

---

## Overview

### Goals
- Simplify video transcripts for 8, 9, and 11-year-old children
- Create structured summaries with Q&A sections
- Enable parent to curate educational content
- Deploy as accessible web app: "School of Knowledge Capital"

### Success Criteria
- Summaries readable at Grade 5-6 level
- Cost < $0.03 per video summary
- Kids can independently browse and learn
- Accessible from any device (iPad, phone, computer)

---

## Requirements

### Functional Requirements
1. **Batch Processing**: Summarize multiple videos at once
2. **Template-Based**: Different prompts for tech, finance, educational content
3. **Structured Output**:
   - Summary (2-3 sentences)
   - Key Points (bullet list)
   - Q&A Section (What? Why? How? What can I learn?)
4. **Cost Tracking**: Monitor spending on API calls
5. **Web Interface**: Kid-friendly viewer accessible via Vercel

### Non-Functional Requirements
- Reading Level: Grade 5-6 (Flesch-Kincaid 5.0-6.0)
- Cost Budget: $10/month maximum
- Performance: Process 10 videos in < 2 minutes
- Availability: Web viewer works 24/7 via Vercel

### Constraints
- Use OpenRouter (budget-friendly models)
- No OpenAI models (per project requirements)
- API key stored in .env only
- Summaries must be offline-accessible (saved as .md files)

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                        │
│  videodistiller summarize --all | <id> | --tag bitcoin │
│  videodistiller serve                                   │
│  videodistiller deploy                                  │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴──────────┬──────────────────┐
        │                      │                  │
        ▼                      ▼                  ▼
┌───────────────┐    ┌──────────────┐    ┌──────────────┐
│   Analyzer    │    │  Prompt      │    │  OpenRouter  │
│   Detector    │───▶│  Builder     │───▶│  Client      │
│               │    │              │    │              │
└───────────────┘    └──────────────┘    └──────┬───────┘
        │                                        │
        │                                        ▼
        │                              ┌──────────────────┐
        │                              │  Response Parser │
        │                              │  & Validator     │
        │                              └────────┬─────────┘
        │                                       │
        ▼                                       ▼
┌─────────────────────────────────────────────────────────┐
│              Summary Storage (data/summaries/)          │
│  - <video-id>.md files                                  │
│  - cost_log.json                                        │
│  - failed.json                                          │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│          Web Generator & Vercel Deployment              │
│  - Generate static site / Next.js app                   │
│  - Deploy to knowledge-capital.vercel.app               │
└─────────────────────────────────────────────────────────┘
```

### New Components

**1. `src/llm/openrouter.py`** - OpenRouter API Client
- Authentication with API key
- Token counting and cost estimation
- Rate limiting and retry logic
- Error handling

**2. `src/llm/prompts.py`** - Template Library
- General template (default)
- Tech/AI template (for AI, coding, technology videos)
- Finance template (for bitcoin, trading, money videos)
- Template selection based on video tags/title

**3. `src/llm/analyzer.py`** - Main Analysis Logic
- Orchestrates: load → detect → prompt → call → save
- Manages batch processing
- Tracks costs and updates logs

**4. `src/llm/detector.py`** - Content Type Detector
- Analyzes tags, title, description
- Returns: 'tech', 'finance', 'educational', 'general'

**5. `src/web/generator.py`** - Static Site Generator
- Converts summaries to HTML
- Creates index page with video grid
- Generates category pages

**6. `src/web/deploy.py`** - Vercel Deployment
- Pushes to git
- Triggers Vercel deployment
- Optionally: direct Vercel API integration

### CLI Commands

```bash
# Summarization
videodistiller summarize --all                    # All videos
videodistiller summarize <video-id>              # Single video
videodistiller summarize --tag bitcoin           # Filtered by tag
videodistiller summarize --retry-failed          # Retry previous failures

# Web Viewer
videodistiller serve                             # Open local viewer
videodistiller build-web                         # Regenerate HTML
videodistiller deploy                            # Deploy to Vercel

# Cost Management
videodistiller cost                              # Show spending summary
videodistiller cost --estimate --all             # Estimate before running
```

---

## Prompt Templates

### Template Selection Logic

```python
def detect_template(video: VideoMetadata) -> str:
    tags_lower = [tag.lower() for tag in video.tags]
    title_lower = video.title.lower()

    # Tech/AI keywords
    tech_keywords = ['ai', 'artificial intelligence', 'coding', 'programming',
                     'technology', 'computer', 'machine learning', 'chatgpt']
    if any(kw in tags_lower or kw in title_lower for kw in tech_keywords):
        return 'tech'

    # Finance keywords
    finance_keywords = ['bitcoin', 'crypto', 'trading', 'stock', 'money',
                        'investment', 'finance', 'business']
    if any(kw in tags_lower or kw in title_lower for kw in finance_keywords):
        return 'finance'

    return 'general'
```

### General Template

```markdown
You are helping a parent explain YouTube videos to their 5th-6th grade children (ages 9-11).

TRANSCRIPT:
{transcript}

VIDEO INFO:
Title: {title}
Channel: {channel}
Duration: {duration}

TASK:
Create a summary at a Grade 5-6 reading level. Use simple words and short sentences.

FORMAT:
## Summary
[2-3 sentences explaining what this video is about in simple terms]

## Key Points
- [Main idea 1 - one sentence]
- [Main idea 2 - one sentence]
- [Main idea 3 - one sentence]
- [If applicable, 1-2 more points]

## Questions & Answers

**What is this about?**
[Explain the main topic in 2-3 simple sentences]

**Why does this matter?**
[Explain why this is important or interesting in real life - 2-3 sentences]

**How does it work?**
[Explain the key process or mechanism simply - 2-3 sentences]

**What can I learn from this?**
[Practical takeaways or lessons - 2-3 sentences]

RULES:
- Use words a 5th grader knows
- Short sentences (10-15 words max)
- Use examples kids understand
- No jargon or technical terms (or explain them simply)
- Be enthusiastic but accurate
```

### Tech/AI Template

```markdown
You are helping a parent explain technology and AI videos to their 5th-6th grade children.

TRANSCRIPT:
{transcript}

VIDEO INFO:
Title: {title}
Channel: {channel}
Duration: {duration}

TASK:
Create a summary at a Grade 5-6 reading level. Focus on making technical concepts understandable.

FORMAT:
[Same as general template]

## Questions & Answers

**What is this about?**
[Explain the technology simply]

**Why does this matter?**
[Real-world impact - how does this affect everyday life?]

**How does it work?**
[IMPORTANT: Use analogies kids understand. Example: "AI is like a super-fast pattern finder,
like how you recognize your friend's face in a crowd."]

**What can I learn from this?**
[Skills, knowledge, or ways to think about technology]

RULES:
- Use everyday analogies (comparing AI to things kids know)
- Explain any tech words you must use
- Make it exciting but not scary
- Connect to things kids use (games, apps, phones)
```

### Finance Template

```markdown
You are helping a parent explain money and business videos to their 5th-6th grade children.

TRANSCRIPT:
{transcript}

VIDEO INFO:
Title: {title}
Channel: {channel}
Duration: {duration}

TASK:
Create a summary at a Grade 5-6 reading level. Connect financial concepts to things kids understand.

FORMAT:
[Same as general template]

## Questions & Answers

**What is this about?**
[Explain the money/business concept simply]

**Why does this matter?**
[IMPORTANT: Connect to kids' lives - allowance, saving, value, choices]

**How does it work?**
[Explain the mechanism using simple examples like lemonade stands, trading cards, etc.]

**What can I learn from this?**
[Money lessons applicable to kids: saving, value, making choices]

RULES:
- Use money examples kids know (allowance, toys, games)
- Explain concepts through stories or examples
- Avoid scary words like "crash" or "lose" without context
- Focus on learning, not fear
- Make complex ideas concrete (use specific dollar amounts kids relate to)
```

---

## OpenRouter Integration

### Configuration

**Environment Variables** (.env):
```bash
# Phase 1 (existing)
YOUTUBE_API_KEY=...

# Phase 2 (new)
OPENROUTER_API_KEY=your_openrouter_key_here
LLM_MODEL=qwen/qwen-2.5-72b-instruct
MAX_MONTHLY_COST=10.00
WARN_AT_COST=8.00
```

### Recommended Models

| Model | Cost per 1M tokens | Quality | Use Case |
|-------|-------------------|---------|----------|
| qwen/qwen-2.5-72b-instruct | $0.35 | High | Default (best balance) |
| deepseek/deepseek-chat | $0.14 | Medium | Budget mode |
| anthropic/claude-3-haiku | $0.80 | Excellent | High-quality (fallback) |

**Cost Estimates** (per video):
- Short video (5 min, ~1500 words): $0.005-0.01
- Medium video (20 min, ~6000 words): $0.02-0.03
- Long video (60 min, ~18000 words): $0.06-0.08

**Monthly Budget Example** ($10/month):
- Can summarize ~300-500 videos per month
- Or ~10-15 videos per day

### API Client Implementation

```python
# src/llm/openrouter.py

import os
import requests
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    cost: float
    model: str

class OpenRouterClient:
    def __init__(self, api_key: str, model: str = "qwen/qwen-2.5-72b-instruct"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"

    def generate(self, prompt: str, max_tokens: int = 2000) -> LLMResponse:
        """Send prompt to OpenRouter and get response."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        data = response.json()
        usage = data["usage"]

        # Calculate cost (pricing varies by model)
        cost = self._calculate_cost(usage["prompt_tokens"], usage["completion_tokens"])

        return LLMResponse(
            text=data["choices"][0]["message"]["content"],
            input_tokens=usage["prompt_tokens"],
            output_tokens=usage["completion_tokens"],
            cost=cost,
            model=self.model
        )

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on model pricing."""
        # Qwen 2.5 72B: $0.35 per 1M tokens (both input/output)
        if "qwen" in self.model:
            rate = 0.35 / 1_000_000
            return (input_tokens + output_tokens) * rate

        # DeepSeek: $0.14 per 1M tokens
        elif "deepseek" in self.model:
            rate = 0.14 / 1_000_000
            return (input_tokens + output_tokens) * rate

        # Default fallback
        return 0.0
```

### Cost Tracking

**Schema** (data/summaries/cost_log.json):
```json
{
  "total_cost": 0.47,
  "total_videos": 15,
  "total_input_tokens": 125000,
  "total_output_tokens": 18000,
  "last_updated": "2025-11-20T14:30:00",
  "monthly_costs": {
    "2025-11": 0.47
  },
  "summaries": [
    {
      "video_id": "S3XGlgNRWbM",
      "title": "Google Nano Banana Pro",
      "timestamp": "2025-11-20T12:16:00",
      "model": "qwen/qwen-2.5-72b-instruct",
      "input_tokens": 7500,
      "output_tokens": 850,
      "cost": 0.029,
      "duration_seconds": 3.2
    }
  ]
}
```

---

## Error Handling

### Missing Transcripts

**Problem**: Video extracted but no transcript available
**Solution**: Create metadata-only summary

```python
def handle_no_transcript(video: VideoMetadata) -> str:
    """Create basic summary from title, description, tags only."""
    return f"""
# {video.title}

**Channel:** {video.channel_title} | **Duration:** {video.duration}s

## What We Know

This video doesn't have a transcript available, but here's what we can tell from the title and description:

**Topic:** {infer_topic_from_title(video.title)}

**Description:**
{simplify_description(video.description)}

**Tags:**
{', '.join(video.tags[:10])}

**To Learn More:**
Watch the video directly: https://youtube.com/watch?v={video.id}
"""
```

### Very Long Videos (>2 hours)

**Problem**: Transcripts > 50,000 characters may exceed context limits or cost too much
**Solutions**:

1. **Warn Before Processing**:
```python
if len(transcript.text) > 50000:
    estimated_cost = estimate_cost(len(transcript.text))
    print(f"⚠️  Long video detected")
    print(f"   Estimated cost: ${estimated_cost:.2f}")
    confirm = input("   Continue? (y/n): ")
    if confirm.lower() != 'y':
        return None
```

2. **Chunked Summarization** (Phase 3 enhancement):
   - Split into 10-minute segments
   - Summarize each chunk
   - Combine summaries into master summary

### API Failures

**Retry Logic**:
```python
def generate_with_retry(client, prompt, max_retries=3):
    """Retry API calls with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return client.generate(prompt)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait_time)
    return None
```

**Failed Video Tracking** (data/summaries/failed.json):
```json
{
  "failed": [
    {
      "video_id": "abc123",
      "title": "Some Video",
      "error": "Rate limit exceeded",
      "timestamp": "2025-11-20T14:00:00",
      "retries": 3
    }
  ]
}
```

**Recovery Command**:
```bash
videodistiller summarize --retry-failed
```

### Quality Validation

**Readability Check**:
```python
from textstat import flesch_kincaid_grade

def validate_reading_level(summary_text: str) -> bool:
    """Ensure summary is at Grade 5-6 level."""
    grade = flesch_kincaid_grade(summary_text)

    if grade > 7.0:
        logger.warning(f"Summary too complex (Grade {grade:.1f})")
        return False

    return True
```

**Regeneration on Quality Failure**:
```python
if not validate_reading_level(summary):
    # Retry with "even simpler" prompt modifier
    prompt = simplify_prompt(original_prompt)
    summary = client.generate(prompt)
```

---

## Data Flow

### Complete Processing Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  1. USER COMMAND                                                 │
│     $ videodistiller summarize --all                             │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│  2. LOAD VIDEOS                                                  │
│     - Read data/metadata/*.json                                  │
│     - Filter: only videos with transcripts                       │
│     - Skip: already summarized (unless --force)                  │
│     Result: List of videos to process                            │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│  3. ESTIMATE COST                                                │
│     - Count total tokens across all transcripts                  │
│     - Calculate estimated cost                                   │
│     - Check against budget (MAX_MONTHLY_COST)                    │
│     - Warn if approaching limit                                  │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│  4. FOR EACH VIDEO                                               │
│     ┌──────────────────────────────────────────────────────────┐ │
│     │ 4a. Detect Content Type                                  │ │
│     │     - Analyze tags, title                                │ │
│     │     - Return: 'tech', 'finance', 'general'               │ │
│     └────────────────┬─────────────────────────────────────────┘ │
│                      ▼                                            │
│     ┌──────────────────────────────────────────────────────────┐ │
│     │ 4b. Build Prompt                                         │ │
│     │     - Select template based on content type              │ │
│     │     - Fill template with transcript + metadata           │ │
│     └────────────────┬─────────────────────────────────────────┘ │
│                      ▼                                            │
│     ┌──────────────────────────────────────────────────────────┐ │
│     │ 4c. Call OpenRouter API                                  │ │
│     │     - Send prompt                                        │ │
│     │     - Retry on failure (3x with backoff)                 │ │
│     │     - Track tokens and cost                              │ │
│     └────────────────┬─────────────────────────────────────────┘ │
│                      ▼                                            │
│     ┌──────────────────────────────────────────────────────────┐ │
│     │ 4d. Validate Response                                    │ │
│     │     - Check reading level (Grade 5-6)                    │ │
│     │     - Verify all sections present                        │ │
│     │     - Regenerate if quality issues                       │ │
│     └────────────────┬─────────────────────────────────────────┘ │
│                      ▼                                            │
│     ┌──────────────────────────────────────────────────────────┐ │
│     │ 4e. Save Summary                                         │ │
│     │     - Write to data/summaries/<video-id>.md              │ │
│     │     - Update cost_log.json                               │ │
│     │     - Show progress: "✓ 3/10 videos"                     │ │
│     └──────────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  5. SHOW SUMMARY                                                 │
│     ✓ Summarized 10 videos                                      │
│     💰 Total cost: $0.24                                         │
│     📊 Monthly spending: $0.71 / $10.00                          │
│     📁 Saved to: data/summaries/                                 │
└──────────────────────────────────────────────────────────────────┘
```

### Directory Structure (Updated)

```
videodistiller/
├── data/
│   ├── metadata/              # Phase 1 - Raw video data
│   │   ├── S3XGlgNRWbM.json
│   │   └── videos.json
│   ├── transcripts/           # Phase 1 - Full transcripts
│   │   └── S3XGlgNRWbM.txt
│   └── summaries/             # Phase 2 - NEW
│       ├── S3XGlgNRWbM.md    # Kid-friendly summaries
│       ├── JyECrGp-Sw8.md
│       ├── cost_log.json      # Spending tracker
│       └── failed.json        # Failed summaries
│
├── src/
│   ├── core/                  # Phase 1 (existing)
│   ├── providers/             # Phase 1 (existing)
│   ├── pipeline/              # Phase 1 (existing)
│   ├── cli/                   # Phase 1 (existing) + new commands
│   ├── utils/                 # Phase 1 (existing)
│   ├── llm/                   # Phase 2 - NEW
│   │   ├── __init__.py
│   │   ├── openrouter.py     # API client
│   │   ├── prompts.py        # Template library
│   │   ├── analyzer.py       # Main orchestrator
│   │   └── detector.py       # Content type detection
│   └── web/                   # Phase 2 - NEW
│       ├── __init__.py
│       ├── generator.py      # HTML generator
│       ├── templates/        # HTML templates
│       └── deploy.py         # Vercel deployment
│
└── docs/
    └── plans/
        ├── 2025-11-20-phase1-mvp-implementation.md
        └── 2025-11-20-phase2-llm-summarization-design.md  # This doc
```

---

## Web Viewer

### Design Principles
- **Kid-Friendly**: Big fonts, colorful, emoji icons
- **Simple Navigation**: No complex menus
- **Fast Loading**: Static site, works offline
- **Mobile-First**: Works on iPad, phone, computer
- **Accessible**: WCAG AA compliance for readability

### Pages

#### 1. Homepage (Index)

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  🎓 School of Knowledge Capital                         │
│  "Learn Something New Every Day!"                       │
│                                                         │
│  📊 Dashboard                                           │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │ 📚 Videos    │ 🎯 Topics    │ ⏱️ Watch Time │        │
│  │    15        │     5        │  4h 32m      │        │
│  └──────────────┴──────────────┴──────────────┘        │
│                                                         │
│  🆕 Latest Videos                                       │
│  ┌────────────────────────────────────────────┐        │
│  │ 🤖 Google Nano Banana Pro                  │        │
│  │ AI can now make super realistic pictures!  │        │
│  │                                             │        │
│  │ By: aiwithbrandon | 24 minutes             │        │
│  │ 📱 Tech & AI | Grade 5-6                   │        │
│  │                                             │        │
│  │ [Read Summary →]                            │        │
│  └────────────────────────────────────────────┘        │
│                                                         │
│  🏷️ Browse by Topic                                    │
│  ┌──────────┬──────────┬──────────┬──────────┐        │
│  │ 🔬 Tech  │ 💰 Money │ 🌍 World │ 📖 More  │        │
│  │   (8)    │   (5)    │   (2)    │   ...    │        │
│  └──────────┴──────────┴──────────┴──────────┘        │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- Video cards with thumbnails (from YouTube)
- Category badges with emoji icons
- Search bar (filter by title/topic)
- Sort options (newest, longest, topic)

#### 2. Summary Page

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  [← Back to Videos]                                     │
│                                                         │
│  🤖 Google Nano Banana Pro: AI Images                  │
│  By aiwithbrandon | 24 minutes | 📱 Tech & AI          │
│                                                         │
│  📝 Summary                                             │
│  Google released a new AI that creates super           │
│  realistic images. It's so good you can't tell         │
│  what's real and what's AI anymore!                    │
│                                                         │
│  💡 Key Points                                          │
│  • The AI is called "Nano Banana Pro"                  │
│  • It makes pictures that look totally real            │
│  • Even experts have trouble telling the difference    │
│  • The technology keeps getting better                 │
│                                                         │
│  ❓ Questions & Answers                                │
│                                                         │
│  **What is this about?**                               │
│  This video shows Google's new AI that...              │
│                                                         │
│  **Why does this matter?**                             │
│  AI image generation is changing how...                │
│                                                         │
│  **How does it work?**                                 │
│  The AI looks at millions of pictures and...           │
│                                                         │
│  **What can I learn from this?**                       │
│  Technology is getting very powerful...                │
│                                                         │
│  🎬 Want to see the original?                          │
│  [Watch on YouTube →]                                  │
│                                                         │
│  [← Previous Video] [Next Video →]                     │
└─────────────────────────────────────────────────────────┘
```

#### 3. Topic/Category Page

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  [← Back to All Topics]                                 │
│                                                         │
│  🔬 Tech & AI Videos                                    │
│  8 videos about technology and artificial intelligence │
│                                                         │
│  [Video Card 1]                                         │
│  [Video Card 2]                                         │
│  [Video Card 3]                                         │
│  ...                                                    │
└─────────────────────────────────────────────────────────┘
```

### Technical Implementation

**Option 1: Static HTML Generator (Simpler)**
```python
# src/web/generator.py

def generate_static_site():
    """Generate complete static HTML site from summaries."""

    # Load all summaries
    summaries = load_all_summaries()

    # Generate index.html
    generate_index(summaries)

    # Generate individual summary pages
    for summary in summaries:
        generate_summary_page(summary)

    # Generate category pages
    categories = group_by_category(summaries)
    for category, videos in categories.items():
        generate_category_page(category, videos)

    # Copy static assets (CSS, JS)
    copy_static_assets()

    print(f"✓ Generated site in data/web/")
    print(f"  Open: data/web/index.html")
```

**Option 2: Next.js App (Better for Vercel)**
```
knowledge-capital/          # Separate Next.js project
├── pages/
│   ├── index.js           # Homepage
│   ├── videos/
│   │   └── [id].js        # Dynamic summary pages
│   └── topics/
│       └── [topic].js     # Category pages
├── components/
│   ├── VideoCard.js
│   ├── SummaryView.js
│   └── Navigation.js
├── public/
│   └── summaries/         # JSON data from videodistiller
└── package.json
```

**Data Sync**:
```bash
# videodistiller exports summaries as JSON
$ videodistiller export-web --format json --output ../knowledge-capital/public/summaries/

# Next.js app reads from public/summaries/
# Deployed to Vercel automatically on git push
```

### Styling (Kid-Friendly CSS)

```css
:root {
  /* Bright, cheerful colors */
  --primary: #4A90E2;      /* Friendly blue */
  --success: #7ED321;      /* Happy green */
  --warning: #F5A623;      /* Warm orange */
  --danger: #D0021B;       /* Important red */

  /* Soft backgrounds */
  --bg-light: #F8F9FA;
  --bg-white: #FFFFFF;

  /* Readable text */
  --text-dark: #2C3E50;
  --text-light: #7F8C8D;
}

body {
  font-family: 'Comic Sans MS', 'Segoe UI', Arial, sans-serif;
  font-size: 18px;         /* Larger for kids */
  line-height: 1.6;
  color: var(--text-dark);
  background: var(--bg-light);
}

h1 {
  font-size: 2.5rem;
  color: var(--primary);
  margin-bottom: 1rem;
}

.video-card {
  background: white;
  border-radius: 16px;      /* Rounded corners */
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.video-card:hover {
  transform: translateY(-4px);  /* Lift on hover */
  box-shadow: 0 8px 12px rgba(0,0,0,0.15);
}

.category-badge {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
  background: var(--primary);
  color: white;
}

/* Emoji icons for visual interest */
.emoji-icon {
  font-size: 2rem;
  margin-right: 8px;
}
```

---

## Deployment Strategy

### Phase 2A: Local Viewer (Immediate)

**Setup** (5 minutes):
```bash
# Generate static site
$ videodistiller build-web

# Open in browser
$ videodistiller serve
# Opens: http://localhost:8000
```

**Pros**:
- Instant setup
- No deployment needed
- Works offline
- Free

**Cons**:
- Only accessible on your computer
- Kids need to ask you to open it
- No remote access

### Phase 2B: Vercel Deployment (Recommended)

**Setup** (15 minutes first time, automatic after):

**Step 1: Create Next.js App**
```bash
# In a separate directory
$ npx create-next-app@latest knowledge-capital
$ cd knowledge-capital
```

**Step 2: Configure Data Sync**
```bash
# In videodistiller
$ videodistiller export-web --output ../knowledge-capital/public/data/

# Or automatic sync
$ videodistiller watch --export-web ../knowledge-capital/public/data/
```

**Step 3: Deploy to Vercel**
```bash
$ cd knowledge-capital
$ vercel deploy

# Follow prompts:
# - Link to Vercel account
# - Choose project name: knowledge-capital
# - Deploy!

# Result: https://knowledge-capital.vercel.app
```

**Workflow After Setup**:
```bash
# You: Extract and summarize videos
$ videodistiller extract --url "..."
$ videodistiller summarize --all
$ videodistiller deploy  # Pushes to Vercel

# Kids: Open bookmark
# https://knowledge-capital.vercel.app
```

**Pros**:
- Accessible from any device
- Kids can browse independently
- Automatic updates when you add videos
- Free on Vercel (hobby plan)
- Fast loading (CDN)

**Cons**:
- Initial setup more complex
- Requires git + Vercel account (you already have)

### Phase 3: Supabase Integration (Future)

**Features to Add**:
- **User Profiles**: Track which kid read which video
- **Progress Tracking**: "8/15 videos completed"
- **Favorites**: Kids can bookmark videos
- **Search**: Full-text search across all summaries
- **Comments**: Kids can leave notes/questions

**Database Schema**:
```sql
-- users table
create table users (
  id uuid primary key,
  name text,
  age int,
  avatar text
);

-- reading_progress table
create table reading_progress (
  user_id uuid references users(id),
  video_id text,
  completed_at timestamp,
  favorite boolean default false
);

-- summaries table (migrated from JSON files)
create table summaries (
  video_id text primary key,
  title text,
  channel text,
  summary_text text,
  qa_data jsonb,
  created_at timestamp
);
```

**Not needed for Phase 2, but easy to add later.**

---

## Implementation Plan

### Task Breakdown

**Phase 2A: Core Summarization (5-7 days)**

**Task 1: OpenRouter Integration**
- Create `src/llm/openrouter.py`
- Implement API client with retry logic
- Add cost calculation
- Write unit tests
- Estimated: 1 day

**Task 2: Prompt Templates**
- Create `src/llm/prompts.py`
- Implement general, tech, finance templates
- Add template selection logic
- Test with sample transcripts
- Estimated: 1 day

**Task 3: Content Analyzer**
- Create `src/llm/analyzer.py`
- Implement batch processing
- Add cost tracking
- Handle errors and retries
- Estimated: 1-2 days

**Task 4: CLI Commands**
- Add `summarize` command to `src/cli/main.py`
- Implement filtering (--all, --tag, etc.)
- Add progress indicators
- Test with real videos
- Estimated: 1 day

**Task 5: Quality Validation**
- Add reading level checker
- Implement regeneration logic
- Add summary validation tests
- Estimated: 1 day

**Phase 2B: Web Viewer (3-5 days)**

**Task 6: Static Site Generator**
- Create `src/web/generator.py`
- Build HTML templates
- Generate index and summary pages
- Add CSS styling
- Estimated: 2 days

**Task 7: Vercel Deployment**
- Set up Next.js project
- Configure data sync
- Deploy to Vercel
- Test on multiple devices
- Estimated: 1-2 days

**Task 8: Testing & Refinement**
- Test with kids (8, 9, 11 year olds)
- Gather feedback on readability
- Adjust templates based on feedback
- Polish UI/UX
- Estimated: 1 day

### Total Estimated Time: 8-12 days

### Success Metrics

**Technical**:
- ✅ Summaries generated at Grade 5-6 level (Flesch-Kincaid 5.0-6.0)
- ✅ Average cost < $0.03 per video
- ✅ 95%+ success rate (failures logged and recoverable)
- ✅ Web viewer loads in < 2 seconds

**User Experience**:
- ✅ Kids can browse and read independently
- ✅ Summaries are understandable without parent explanation
- ✅ Kids ask questions or share learnings from videos
- ✅ Positive feedback from 8, 9, 11 year olds

---

## Appendix

### Example Summary Output

**File**: `data/summaries/S3XGlgNRWbM.md`

```markdown
# Google Nano Banana Pro: MIND-BLOWING AI Images

**Video by:** aiwithbrandon
**Duration:** 24 minutes 28 seconds
**Topic:** 🤖 Tech & AI
**Reading Level:** Grade 5-6
**Summarized:** November 20, 2025

---

## Summary

Google just released a new AI called Nano Banana Pro that can create super realistic images. The AI is so good that you can't tell if a picture is real or made by a computer. This technology is getting better every day and changing how we think about photos and art.

## Key Points

- Nano Banana Pro is Google's newest AI for making images
- The AI creates pictures that look completely real
- Even experts have trouble telling AI images from real photos
- The technology uses patterns it learned from millions of pictures
- This AI is much better than older versions

## Questions & Answers

### What is this about?

This video shows Google's new artificial intelligence called Nano Banana Pro. AI is like a super-smart computer program that can learn and create things. This particular AI makes pictures that look so real, you can't tell they were made by a computer. The person in the video shows lots of examples where even he couldn't tell which picture was real!

### Why does this matter?

This technology matters because it's changing how we create and think about images. In the future, artists, game designers, and movie makers could use AI to help create amazing visuals. But it also means we need to be careful - if AI can make fake pictures that look real, we need to think about what's true and what's created. It's like having a super-powered camera that can make anything you imagine!

### How does it work?

The AI works like a really smart pattern finder. Imagine if you looked at millions of pictures of dogs - you'd start to notice patterns like "dogs have four legs" and "dog noses are usually black." The AI does the same thing but way faster! It looks at tons of images and learns what makes pictures look real. Then when you ask it to make a new image, it uses all those patterns to create something that follows the rules it learned.

### What can I learn from this?

You can learn that technology is getting very powerful and can do things that seem like magic. But it's not magic - it's math and patterns! This also teaches us to think carefully about what we see. Just because a picture looks real doesn't mean it is real anymore. It's important to ask questions and think critically about images we see online. Technology is a tool that can help us create amazing things, but we need to use it responsibly.

---

**Want to watch the original video?**
[Open on YouTube →](https://youtube.com/watch?v=S3XGlgNRWbM)

**Tags:** AI, artificial intelligence, Google, image generation, technology, Nano Banana Pro, machine learning

---

*This summary was created to help kids (ages 8-12) learn from videos their parents save. Made with ❤️ by Dad.*
```

### Environment Setup Checklist

```bash
# Phase 1 (Already Complete)
✅ YOUTUBE_API_KEY configured
✅ Data directories created
✅ Extract videos working

# Phase 2 Setup
⬜ Get OpenRouter API key
   Visit: https://openrouter.ai/keys
   Free tier: $1 credit to start

⬜ Add to .env file:
   OPENROUTER_API_KEY=sk-or-...
   LLM_MODEL=qwen/qwen-2.5-72b-instruct
   MAX_MONTHLY_COST=10.00

⬜ Test summarization:
   videodistiller summarize <video-id>

⬜ Generate web viewer:
   videodistiller build-web

⬜ Deploy to Vercel:
   videodistiller deploy
```

---

**End of Design Document**

**Next Steps:**
1. Review and approve design
2. Set up git worktree for implementation
3. Create detailed implementation plan
4. Begin Task 1: OpenRouter Integration
