#!/usr/bin/env bash
set -euo pipefail

source "Porting/Tools/Common.sh"

python_cmd="$(require_python_cmd)"
toolchain_name="${TOOLCHAIN_NAME:-}"
toolchain_url="${TOOLCHAIN_URL:-}"
toolchain_archive="${TOOLCHAIN_ARCHIVE:-}"
toolchain_install_dir="${TOOLCHAIN_INSTALL_DIR:-}"

if [[ -z "$toolchain_url" || -z "$toolchain_install_dir" ]]; then
  while IFS='=' read -r key value; do
    case "$key" in
      TOOLCHAIN_NAME)
        [[ -n "$toolchain_name" ]] || toolchain_name="$value"
        ;;
      TOOLCHAIN_URL)
        [[ -n "$toolchain_url" ]] || toolchain_url="$value"
        ;;
      TOOLCHAIN_ARCHIVE)
        [[ -n "$toolchain_archive" ]] || toolchain_archive="$value"
        ;;
      TOOLCHAIN_INSTALL_DIR)
        [[ -n "$toolchain_install_dir" ]] || toolchain_install_dir="$value"
        ;;
    esac
  done < <("$python_cmd" Porting/Tools/ExportPortConfig.py)
fi

if [[ -z "$toolchain_url" || -z "$toolchain_install_dir" ]]; then
  echo "missing toolchain config" >&2
  exit 1
fi

if [[ -z "$toolchain_archive" ]]; then
  toolchain_archive="$(basename "$toolchain_url")"
fi

toolchain_install_dir="${toolchain_install_dir/#\$HOME/$HOME}"
archive_path="${RUNNER_TEMP:-$PWD}/${toolchain_archive}"

mkdir -p "$toolchain_install_dir"
rm -f "$archive_path"

if command -v curl >/dev/null 2>&1; then
  curl -L --fail --retry 3 "$toolchain_url" -o "$archive_path"
elif command -v wget >/dev/null 2>&1; then
  wget -O "$archive_path" "$toolchain_url"
else
  echo "missing downloader for toolchain" >&2
  exit 1
fi

tar -zxf "$archive_path" -C "$toolchain_install_dir"

toolchain_bin="$(find "$toolchain_install_dir" -type d -name bin | head -n 1)"
if [[ -z "$toolchain_bin" ]]; then
  toolchain_bin="$toolchain_install_dir/bin"
fi

if [[ -n "${GITHUB_PATH:-}" ]]; then
  printf '%s\n' "$toolchain_bin" >> "$GITHUB_PATH"
fi

printf 'toolchain_name=%s\n' "${toolchain_name:-unknown}"
printf 'toolchain_url=%s\n' "$toolchain_url"
printf 'toolchain_install_dir=%s\n' "$toolchain_install_dir"
printf 'toolchain_bin=%s\n' "$toolchain_bin"
