#!/usr/bin/env bash
set -euo pipefail

# Run post-processing suite for phase2 artifacts.
# Usage: Run_Postprocess_Suite.sh

source "Tools/Porting/Common.sh"
python_cmd="$(require_python_cmd)" || exit 1

if [[ ! -f artifacts/run-meta.txt ]]; then
  git_sha=""
  git_ref=""
  if command -v git >/dev/null 2>&1; then
    git_sha="$(git rev-parse --short=12 HEAD 2>/dev/null || true)"
    git_ref="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  fi
  {
    echo "workflow=local-postprocess"
    echo "run_id=local"
    echo "run_number=local"
    echo "sha=${git_sha}"
    echo "ref=${git_ref}"
    echo "device=umi"
    echo "source_repo=local"
    echo "source_branch="
    echo "target_repo=local"
    echo "target_branch="
  } > artifacts/run-meta.txt
fi

steps=(
  "Build_Runtime_Validation_Template.py"
  "Parse_Runtime_Validation_Input.py"
  "Init_Driver_Integration_Manifest.py"
  "Build_Driver_Integration_Evidence.py"
  "Sync_Driver_Integration_Manifest.py"
  "Validate_Driver_Integration_Manifest.py"
  "Validate_Anykernel_Candidate.py"
  "Validate_Boot_Image.py"
  "Evaluate_Artifact.py"
  "Check_Artifact_Completeness.py"
  "Build_Driver_Integration_Status.py"
  "Build_Phase2_Report.py"
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
  if "$python_cmd" "$script"; then
    echo "${step}=ok" | tee -a "$status_file"
  else
    echo "${step}=failed" | tee -a "$status_file"
  fi
done
