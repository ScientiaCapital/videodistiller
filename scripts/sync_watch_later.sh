#!/bin/bash
# Quick wrapper for Watch Later sync
# Usage: ./scripts/sync_watch_later.sh [extract|summarize|both]

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d "venv/bin" ]; then
    source venv/bin/activate
fi

MODE="${1:-both}"

case "$MODE" in
    extract)
        echo "📥 Extracting Watch Later videos..."
        python3 scripts/watch_later.py --extract
        ;;
    summarize)
        echo "🤖 Summarizing existing videos..."
        python3 scripts/watch_later.py --summarize
        ;;
    both)
        echo "🚀 Full sync: Extract + Summarize..."
        python3 scripts/watch_later.py --extract --summarize
        ;;
    *)
        echo "Usage: $0 [extract|summarize|both]"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
