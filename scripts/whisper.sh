#!/bin/bash
# whisper.sh — wrapper global: selalu pakai venv skill (faster-whisper + av==12.3.0 terpin).
# Bisa dipanggil dari chat/worker/cron mana pun tanpa setup.
# Usage: whisper.sh <vo.wav> [-o timestamps.json] [--lang id] [--model ...]
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
exec "$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/scripts/whisper_timestamps.py" "$@"
