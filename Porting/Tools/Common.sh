#!/usr/bin/env bash

resolve_python_cmd() {
  local cand
  for cand in python python3; do
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys' >/dev/null 2>&1; then
      printf '%s\n' "$cand"
      return 0
    fi
  done
  return 1
}

require_python_cmd() {
  local message="${1:-python interpreter not found}"
  local python_cmd
  python_cmd="$(resolve_python_cmd)" || {
    echo "$message" >&2
    return 1
  }
  printf '%s\n' "$python_cmd"
}

resolve_repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || pwd -P
}

initialize_porting_paths() {
  local repo_root="${1:-$(resolve_repo_root)}"

  export KERNEL_DIR="${KERNEL_DIR:-$repo_root}"
  export REFERENCE_DIR="${REFERENCE_DIR:-$repo_root/source}"
  export PHASE2_PORT_DIR="${PHASE2_PORT_DIR:-$repo_root/artifacts/phase2}"
  export OUT_DIR="${OUT_DIR:-$repo_root/out}"
  export ARTIFACTS_DIR="${ARTIFACTS_DIR:-$repo_root/artifacts}"
}
