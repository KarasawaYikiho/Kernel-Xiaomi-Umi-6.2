#!/usr/bin/env bash
set -euo pipefail

# Run post-processing suite for phase2 artifacts.
# Usage: Run_Postprocess_Suite.sh

steps=(
  "Build_Runtime_Validation_Template.py"
  "Parse_Runtime_Validation_Input.py"
  "Check_Artifact_Completeness.py"
  "Init_Driver_Integration_Manifest.py"
  "Validate_Driver_Integration_Manifest.py"
  "Build_Driver_Integration_Status.py"
  "Build_Phase2_Report.py"
  "Validate_Anykernel_Candidate.py"
  "Validate_Boot_Image.py"
  "Suggest_Next_Focus.py"
  "Verify_Decision_Consistency.py"
  "Extract_Build_Errors.py"
  "Build_Artifact_Index.py"
  "Summarize_Artifacts_Markdown.py"
  "Validate_Phase2_Report.py"
  "Collect_Metrics_Json.py"
  "Build_Status_Badge_Line.py"
  "Build_Artifact_Checksums.py"
  "Build_Action_Validation_Checklist.py"
  "Build_Runtime_Validation_Summary.py"
)

status_file="artifacts/postprocess-status.txt"
mkdir -p "artifacts"
: > "$status_file"

for step in "${steps[@]}"; do
  script="Tools/Porting/${step}"
  if python3 "$script"; then
    echo "${step}=ok" | tee -a "$status_file"
  else
    echo "${step}=failed" | tee -a "$status_file"
  fi
done
