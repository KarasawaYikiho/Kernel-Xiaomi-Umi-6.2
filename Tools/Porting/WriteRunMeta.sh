#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   Write_Run_Meta.sh <run_id> <run_number> <sha> <ref> <device> <source_repo> <source_branch> <target_repo> <target_branch>

mkdir -p artifacts

{
  echo "workflow=${PORT_WORKFLOW_NAME:-phase2-port-sm8250-reference}"
  echo "run_id=${1:-}"
  echo "run_number=${2:-}"
  echo "sha=${3:-}"
  echo "ref=${4:-}"
  echo "device=${5:-}"
  echo "source_repo=${6:-}"
  echo "source_branch=${7:-}"
  echo "target_repo=${8:-}"
  echo "target_branch=${9:-}"
} > artifacts/run-meta.txt
