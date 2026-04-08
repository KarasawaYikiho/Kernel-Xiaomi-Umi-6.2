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
