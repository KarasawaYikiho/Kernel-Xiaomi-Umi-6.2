#!/usr/bin/env bash
set -euo pipefail

# Run post-processing suite for phase2 artifacts.
# Usage: Run_Postprocess_Suite.sh

python3 Tools/Porting/Check_Artifact_Completeness.py || true
python3 Tools/Porting/Validate_Anykernel_Candidate.py || true
python3 Tools/Porting/Validate_Boot_Image.py || true
python3 Tools/Porting/Suggest_Next_Focus.py || true
python3 Tools/Porting/Extract_Build_Errors.py || true
python3 Tools/Porting/Build_Artifact_Index.py || true
python3 Tools/Porting/Summarize_Artifacts_Markdown.py || true
python3 Tools/Porting/Validate_Phase2_Report.py || true
python3 Tools/Porting/Collect_Metrics_Json.py || true
python3 Tools/Porting/Build_Status_Badge_Line.py || true
python3 Tools/Porting/Build_Artifact_Checksums.py || true
python3 Tools/Porting/Build_Action_Validation_Checklist.py || true
