#!/usr/bin/env bash
set -euo pipefail

# Best-effort release boot.img preparation.
# Requires kernel image + ramdisk + mkbootimg parameters.
# Writes artifacts/bootimg-build.txt with explicit blockers when inputs are missing.

ART=artifacts
mkdir -p "$ART"
OUT="$ART/bootimg-build.txt"

kernel_path=""
ramdisk_path="${BOOTIMG_RAMDISK_PATH:-}"
ramdisk_url="${BOOTIMG_RAMDISK_URL:-}"
prebuilt_url="${BOOTIMG_PREBUILT_URL:-}"
dtb_path="${BOOTIMG_DTB_PATH:-}"
mkbootimg_cmd=""

fetch_file() {
  local url="$1"; local out="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 3 "$url" -o "$out" && return 0
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$out" "$url" && return 0
  fi
  return 1
}

# kernel
if [[ -f out/arch/arm64/boot/Image.gz ]]; then
  kernel_path="out/arch/arm64/boot/Image.gz"
elif [[ -f out/arch/arm64/boot/Image ]]; then
  kernel_path="out/arch/arm64/boot/Image"
fi

# ramdisk (mandatory for direct flashable boot.img)
if [[ -z "$ramdisk_path" ]]; then
  for p in \
    "$ART/ramdisk.cpio.gz" \
    "target/ramdisk.cpio.gz" \
    "target/boot/ramdisk.cpio.gz"; do
    [[ -f "$p" ]] && ramdisk_path="$p" && break
  done
fi

# optional download path for ramdisk
if [[ -z "$ramdisk_path" && -n "$ramdisk_url" ]]; then
  ramdisk_dl="$ART/ramdisk-download"
  if fetch_file "$ramdisk_url" "$ramdisk_dl"; then
    # direct ramdisk file
    if file "$ramdisk_dl" 2>/dev/null | grep -Eiq 'gzip compressed|cpio archive'; then
      mv -f "$ramdisk_dl" "$ART/ramdisk.cpio.gz"
      ramdisk_path="$ART/ramdisk.cpio.gz"
    # archive fallback: try to extract a ramdisk payload from zip
    elif [[ "$ramdisk_url" == *.zip* ]] && command -v unzip >/dev/null 2>&1; then
      if unzip -p "$ramdisk_dl" "*ramdisk*.cpio.gz" > "$ART/ramdisk.cpio.gz" 2>/dev/null; then
        ramdisk_path="$ART/ramdisk.cpio.gz"
      elif unzip -p "$ramdisk_dl" "*initramfs*.cpio.gz" > "$ART/ramdisk.cpio.gz" 2>/dev/null; then
        ramdisk_path="$ART/ramdisk.cpio.gz"
      fi
    fi
  fi
fi

# dtb (optional for newer header versions but preferred)
if [[ -z "$dtb_path" && -s "$ART/umi_primary_dtb_paths.txt" ]]; then
  cand="$(head -n1 "$ART/umi_primary_dtb_paths.txt" || true)"
  [[ -f "$cand" ]] && dtb_path="$cand"
fi

# mkbootimg tool detection (with best-effort remote fallback)
if command -v mkbootimg >/dev/null 2>&1; then
  mkbootimg_cmd="mkbootimg"
elif [[ -x "$HOME/.local/bin/mkbootimg" ]]; then
  mkbootimg_cmd="$HOME/.local/bin/mkbootimg"
elif [[ -x "$HOME/.local/bin/mkbootimg.py" ]]; then
  mkbootimg_cmd="$HOME/.local/bin/mkbootimg.py"
elif [[ -f source/Tools/mkbootimg/mkbootimg.py ]]; then
  mkbootimg_cmd="python3 source/Tools/mkbootimg/mkbootimg.py"
elif [[ -f target/Tools/mkbootimg/mkbootimg.py ]]; then
  mkbootimg_cmd="python3 target/Tools/mkbootimg/mkbootimg.py"
elif command -v python3 >/dev/null 2>&1; then
  py_mkbootimg="$(python3 - <<'PY'
import importlib.util
print('ok' if importlib.util.find_spec('mkbootimg') else 'no')
PY
)"
  if [[ "$py_mkbootimg" == "ok" ]]; then
    mkbootimg_cmd="python3 -m mkbootimg"
  fi
fi

# Last resort: fetch a standalone mkbootimg.py into artifacts/ (network best-effort)
if [[ -z "$mkbootimg_cmd" && -x "$(command -v python3 || true)" ]]; then
  fetched="$ART/mkbootimg.py"
  fetch_urls=(
    "https://raw.githubusercontent.com/aosp-mirror/platform_system_tools_mkbootimg/master/mkbootimg.py"
    "https://android.googlesource.com/platform/system/Tools/mkbootimg/+/refs/heads/master/mkbootimg.py?format=TEXT"
  )
  for u in "${fetch_urls[@]}"; do
    if command -v curl >/dev/null 2>&1; then
      if [[ "$u" == *"format=TEXT"* ]]; then
        curl -L --fail --retry 2 "$u" | base64 -d > "$fetched" 2>/dev/null || true
      else
        curl -L --fail --retry 2 "$u" -o "$fetched" || true
      fi
    elif command -v wget >/dev/null 2>&1; then
      if [[ "$u" == *"format=TEXT"* ]]; then
        wget -qO- "$u" | base64 -d > "$fetched" 2>/dev/null || true
      else
        wget -O "$fetched" "$u" || true
      fi
    fi
    if [[ -s "$fetched" ]]; then
      chmod +x "$fetched" || true
      mkbootimg_cmd="python3 '$fetched'"
      break
    fi
  done
fi

header_version="${BOOTIMG_HEADER_VERSION:-3}"
base="${BOOTIMG_BASE:-0x00000000}"
pagesize="${BOOTIMG_PAGESIZE:-4096}"
cmdline="${BOOTIMG_CMDLINE:-}"
required_bytes="${BOOTIMG_REQUIRED_BYTES:-268435456}"

# fallback: use a prebuilt boot.img directly when mkbootimg inputs are unavailable
if [[ -n "$prebuilt_url" ]]; then
  out_boot="$ART/boot.img"
  prebuilt_dl="$ART/prebuilt-download"
  if fetch_file "$prebuilt_url" "$prebuilt_dl"; then
    # direct boot.img
    if file "$prebuilt_dl" 2>/dev/null | grep -Eiq 'Android bootimg|data'; then
      mv -f "$prebuilt_dl" "$out_boot"
    # archive fallback: try to extract boot.img from zip
    elif [[ "$prebuilt_url" == *.zip* ]] && command -v unzip >/dev/null 2>&1; then
      unzip -p "$prebuilt_dl" "*boot.img" > "$out_boot" 2>/dev/null || true
    fi
  fi
  if [[ -f "$out_boot" ]]; then
    size="$(stat -c%s "$out_boot" 2>/dev/null || wc -c < "$out_boot")"
    final_reason="prebuilt-bootimg-downloaded"
    if [[ "$required_bytes" =~ ^[0-9]+$ ]] && [[ "$required_bytes" -gt 0 ]]; then
      if [[ "$size" -lt "$required_bytes" ]]; then
        truncate -s "$required_bytes" "$out_boot"
        size="$required_bytes"
        final_reason="prebuilt-bootimg-downloaded-and-padded"
      elif [[ "$size" -gt "$required_bytes" ]]; then
        final_reason="prebuilt-bootimg-oversize"
      fi
    fi
    {
      echo "status=ok"
      echo "reason=$final_reason"
      echo "missing="
      echo "kernel_path=$kernel_path"
      echo "ramdisk_path=$ramdisk_path"
      echo "dtb_path=$dtb_path"
      echo "mkbootimg_cmd=$mkbootimg_cmd"
      echo "header_version=$header_version"
      echo "base=$base"
      echo "pagesize=$pagesize"
      echo "output=$out_boot"
      echo "output_size_bytes=$size"
      echo "required_bytes=$required_bytes"
      echo "source=prebuilt_url"
      echo "prebuilt_url=$prebuilt_url"
    } > "$OUT"
    echo "bootimg prepared: $out_boot ($size bytes)"
    exit 0
  fi
fi

missing=()
[[ -n "$mkbootimg_cmd" ]] || missing+=("mkbootimg")
[[ -n "$kernel_path" ]] || missing+=("kernel_image")
[[ -n "$ramdisk_path" ]] || missing+=("ramdisk")

if [[ ${#missing[@]} -gt 0 ]]; then
  {
    echo "status=blocked"
    echo "reason=missing-inputs"
    echo "missing=$(IFS=,; echo "${missing[*]}")"
    echo "kernel_path=$kernel_path"
    echo "ramdisk_path=$ramdisk_path"
    echo "dtb_path=$dtb_path"
    echo "mkbootimg_cmd=$mkbootimg_cmd"
    echo "header_version=$header_version"
    echo "base=$base"
    echo "pagesize=$pagesize"
  } > "$OUT"
  echo "bootimg build blocked: $(IFS=,; echo "${missing[*]}")"
  exit 0
fi

# build boot.img into artifacts
out_boot="$ART/boot.img"
set +e
if [[ -n "$dtb_path" && -f "$dtb_path" ]]; then
  eval "$mkbootimg_cmd --kernel '$kernel_path' --ramdisk '$ramdisk_path' --dtb '$dtb_path' --header_version '$header_version' --base '$base' --pagesize '$pagesize' --cmdline '$cmdline' --output '$out_boot'"
  rc=$?
else
  eval "$mkbootimg_cmd --kernel '$kernel_path' --ramdisk '$ramdisk_path' --header_version '$header_version' --base '$base' --pagesize '$pagesize' --cmdline '$cmdline' --output '$out_boot'"
  rc=$?
fi
set -e

if [[ $rc -ne 0 || ! -f "$out_boot" ]]; then
  {
    echo "status=failed"
    echo "reason=mkbootimg-failed"
    echo "missing="
    echo "kernel_path=$kernel_path"
    echo "ramdisk_path=$ramdisk_path"
    echo "dtb_path=$dtb_path"
    echo "mkbootimg_cmd=$mkbootimg_cmd"
    echo "header_version=$header_version"
    echo "base=$base"
    echo "pagesize=$pagesize"
  } > "$OUT"
  exit 0
fi

size="$(stat -c%s "$out_boot" 2>/dev/null || wc -c < "$out_boot")"
final_reason="bootimg-built"
if [[ "$required_bytes" =~ ^[0-9]+$ ]] && [[ "$required_bytes" -gt 0 ]]; then
  if [[ "$size" -lt "$required_bytes" ]]; then
    truncate -s "$required_bytes" "$out_boot"
    size="$required_bytes"
    final_reason="bootimg-built-and-padded"
  elif [[ "$size" -gt "$required_bytes" ]]; then
    final_reason="bootimg-built-oversize"
  fi
fi
{
  echo "status=ok"
  echo "reason=$final_reason"
  echo "missing="
  echo "kernel_path=$kernel_path"
  echo "ramdisk_path=$ramdisk_path"
  echo "dtb_path=$dtb_path"
  echo "mkbootimg_cmd=$mkbootimg_cmd"
  echo "header_version=$header_version"
  echo "base=$base"
  echo "pagesize=$pagesize"
  echo "output=$out_boot"
  echo "output_size_bytes=$size"
  echo "required_bytes=$required_bytes"
} > "$OUT"

echo "bootimg built: $out_boot ($size bytes)"
