#!/usr/bin/env bash
set -euo pipefail

# Run post-processing suite for phase2 artifacts.
# Usage: RunPostprocessSuite.sh

source "Porting/Tools/Common.sh"
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
    echo "device=${DEVICE:-unknown}"
    echo "source_repo=local"
    echo "source_branch="
    echo "target_repo=local"
    echo "target_branch="
  } > artifacts/run-meta.txt
fi

steps=(
  "BuildRuntimeValidationTemplate.py"
  "ParseRuntimeValidationInput.py"
  "InitDriverIntegrationManifest.py"
  "InitRomAlignmentManifest.py"
  "BuildAnyKernelCandidate.sh"
  "BuildDriverIntegrationEvidence.py"
  "BuildDtbManifest.py"
  "ListBuiltDtbPaths.py"
  "DtbPostcheck.py"
  "AnalyzeDtbMiss.py"
  "SyncDriverIntegrationManifest.py"
  "ValidateDriverIntegrationManifest.py"
  "ValidateAnyKernelCandidate.py"
  "PrepareReleaseBootImg.sh"
  "ValidateBootImage.py"
  "SyncRomAlignmentManifest.py"
  "ValidateRomAlignmentManifest.py"
  "EvaluateArtifact.py"
  "CheckArtifactCompleteness.py"
  "BuildDriverIntegrationStatus.py"
  "BuildRomAlignmentStatus.py"
  "BuildPlanProgress.py"
  "BuildPhase2Report.py"
  "SuggestNextFocus.py"
  "VerifyDecisionConsistency.py"
  "ExtractBuildErrors.py"
  "BuildArtifactIndex.py"
  "SummarizeArtifactsMarkdown.py"
  "ValidatePhase2Report.py"
  "CollectMetricsJson.py"
  "BuildStatusBadgeLine.py"
  "BuildArtifactChecksums.py"
  "BuildActionValidationChecklist.py"
  "BuildRuntimeValidationSummary.py"
)

status_file="artifacts/postprocess-status.txt"
mkdir -p "artifacts"
: > "$status_file"

for step in "${steps[@]}"; do
  script="Porting/Tools/${step}"
  if [[ "$script" == *.sh ]]; then
    chmod +x "$script"
    if "$script"; then
      step_rc=0
    else
      step_rc=$?
    fi
  else
    if "$python_cmd" "$script"; then
      step_rc=0
    else
      step_rc=$?
    fi
  fi

  if [[ "$step_rc" -eq 0 ]]; then
    echo "${step}=ok" | tee -a "$status_file"
  else
    echo "${step}=failed" | tee -a "$status_file"
  fi
done
