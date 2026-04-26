#!/usr/bin/env bash
set -euo pipefail

# Normalize BOOTIMG_REQUIRED_BYTES and export a safe integer value.
# Resolution order:
# - Explicit environment override
# - Porting/OfficialRomBaseline/BootImageBaseline.env
# - Porting/OfficialRomAnalysis.md
# - Hard fallback default

DEFAULT_BOOTIMG_REQUIRED_BYTES=134217728
BASELINE_ENV="Porting/OfficialRomBaseline/BootImageBaseline.env"
ROM_ANALYSIS="Porting/OfficialRomAnalysis.md"
raw="${BOOTIMG_REQUIRED_BYTES:-}"
raw="${raw//[[:space:]]/}"

if [[ -z "$raw" ]]; then
  if [[ -f "$BASELINE_ENV" ]]; then
    baseline_raw="$(grep -E '^BOOTIMG_REQUIRED_BYTES=' "$BASELINE_ENV" | head -n 1)"
    baseline_raw="${baseline_raw#BOOTIMG_REQUIRED_BYTES=}"
    baseline_raw="${baseline_raw//[[:space:]]/}"
    if [[ -n "$baseline_raw" ]]; then
      raw="$baseline_raw"
    fi
  fi
fi

if [[ -z "$raw" && -f "$ROM_ANALYSIS" ]]; then
  raw="$(python - "$ROM_ANALYSIS" <<'PY'
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='ignore')
m = re.search(r"`boot\.img`: size=`(\d+)`", text, re.IGNORECASE)
print(m.group(1) if m else "")
PY
)"
  raw="${raw//[[:space:]]/}"
fi

if [[ -z "$raw" ]]; then
  raw="$DEFAULT_BOOTIMG_REQUIRED_BYTES"
fi

if [[ "$raw" =~ ^-?[0-9]+$ ]]; then
  normalized="$raw"
else
  normalized="$DEFAULT_BOOTIMG_REQUIRED_BYTES"
  echo "::warning::Invalid bootimg_required_bytes input '$raw', fallback to $DEFAULT_BOOTIMG_REQUIRED_BYTES"
fi

if [[ -n "${GITHUB_ENV:-}" ]]; then
  echo "BOOTIMG_REQUIRED_BYTES=$normalized" >> "$GITHUB_ENV"
fi
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  echo "bootimg_required_bytes_normalized=$normalized" >> "$GITHUB_OUTPUT"
fi

echo "normalized_bootimg_required_bytes=$normalized"
