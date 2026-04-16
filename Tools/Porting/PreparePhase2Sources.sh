#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   Prepare_Phase2_Sources.sh <source_repo> <source_branch> <target_repo> <target_branch>

SOURCE_REPO="${1:?source_repo required}"
SOURCE_BRANCH="${2:?source_branch required}"
TARGET_REPO="${3:?target_repo required}"
TARGET_BRANCH="${4:?target_branch required}"

extract_archive_to_dir() {
  local archive_path="$1"
  local dest_dir="$2"
  local tmp_dir extracted_root

  [[ -s "$archive_path" ]] || return 1
  tmp_dir="${dest_dir}.extract"
  rm -rf "$tmp_dir" "$dest_dir"
  mkdir -p "$tmp_dir" "$dest_dir"

  if command -v unzip >/dev/null 2>&1; then
    unzip -q "$archive_path" -d "$tmp_dir"
  elif command -v python3 >/dev/null 2>&1; then
    python3 - "$archive_path" "$tmp_dir" <<'PY'
import sys
import zipfile
from pathlib import Path

archive = Path(sys.argv[1])
target = Path(sys.argv[2])
with zipfile.ZipFile(archive) as zf:
    zf.extractall(target)
PY
  elif command -v python >/dev/null 2>&1; then
    python - "$archive_path" "$tmp_dir" <<'PY'
import sys
import zipfile
from pathlib import Path

archive = Path(sys.argv[1])
target = Path(sys.argv[2])
with zipfile.ZipFile(archive) as zf:
    zf.extractall(target)
PY
  else
    return 1
  fi

  extracted_root="$(find "$tmp_dir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  [[ -n "$extracted_root" ]] || return 1
  cp -R "$extracted_root"/. "$dest_dir"/
  rm -rf "$tmp_dir"
}

use_cached_archive_if_present() {
  local archive_path="$1"
  local dest_dir="$2"
  [[ -n "$archive_path" ]] || return 1
  [[ -s "$archive_path" ]] || return 1
  echo "using cached source archive: $archive_path -> $dest_dir"
  extract_archive_to_dir "$archive_path" "$dest_dir"
}

download_and_extract_github_branch() {
  local repo_url="$1"
  local branch="$2"
  local dest_dir="$3"
  local archive_path tmp_dir repo_path download_url extracted_root

  if [[ ! "$repo_url" =~ ^https://github.com/([^/]+)/([^/.]+)(\.git)?$ ]]; then
    return 1
  fi

  repo_path="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
  archive_path="${dest_dir}.zip"
  tmp_dir="${dest_dir}.extract"
  download_url="https://codeload.github.com/${repo_path}/zip/refs/heads/${branch}"

  rm -rf "$tmp_dir" "$archive_path"

  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 3 "$download_url" -o "$archive_path" || true
  fi
  if [[ ! -s "$archive_path" ]] && command -v wget >/dev/null 2>&1; then
    wget -O "$archive_path" "$download_url" || true
  fi
  if [[ ! -s "$archive_path" ]] && command -v powershell >/dev/null 2>&1; then
    powershell -Command "\$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing '$download_url' -OutFile '$archive_path'" || true
  fi
  if [[ ! -s "$archive_path" ]] && command -v pwsh >/dev/null 2>&1; then
    pwsh -Command "\$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing '$download_url' -OutFile '$archive_path'" || true
  fi
  if [[ ! -s "$archive_path" ]] && command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -Command "\$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing '$download_url' -OutFile '$archive_path'" || true
  fi
  if [[ ! -s "$archive_path" ]] && command -v pwsh.exe >/dev/null 2>&1; then
    pwsh.exe -Command "\$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing '$download_url' -OutFile '$archive_path'" || true
  fi
  if [[ ! -s "$archive_path" ]]; then
    return 1
  fi
  extract_archive_to_dir "$archive_path" "$dest_dir"
  rm -f "$archive_path"
}

clone_or_fetch() {
  local repo_url="$1"
  local branch="$2"
  local dest_dir="$3"
  local cache_archive="$4"

  rm -rf "$dest_dir"

  if use_cached_archive_if_present "$cache_archive" "$dest_dir"; then
    return 0
  fi

  if git clone --depth=1 --branch "$branch" "$repo_url" "$dest_dir"; then
    return 0
  fi

  echo "git clone failed for $repo_url#$branch, trying codeload zip fallback"
  download_and_extract_github_branch "$repo_url" "$branch" "$dest_dir"
}

rm -rf source target

clone_or_fetch "$SOURCE_REPO" "$SOURCE_BRANCH" source "${SOURCE_ARCHIVE:-source.zip}"
clone_or_fetch "$TARGET_REPO" "$TARGET_BRANCH" target "${TARGET_ARCHIVE:-target.zip}"
