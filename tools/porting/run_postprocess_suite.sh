#!/usr/bin/env bash
set -euo pipefail

# Run post-processing suite for phase2 artifacts.
# Usage: run_postprocess_suite.sh [quality_gate_mode]
# quality_gate_mode: warn|strict (default: warn)

QUALITY_GATE_MODE="${1:-warn}"

python3 tools/porting/check_artifact_completeness.py || true
python3 tools/porting/suggest_next_focus.py || true
python3 tools/porting/extract_build_errors.py || true
python3 tools/porting/build_artifact_index.py || true
python3 tools/porting/summarize_artifacts_markdown.py || true
python3 tools/porting/validate_phase2_report.py || true
python3 tools/porting/collect_metrics_json.py || true
python3 tools/porting/build_status_badge_line.py || true
python3 tools/porting/build_artifact_checksums.py || true
python3 tools/porting/enforce_quality_gates.py "$QUALITY_GATE_MODE"
