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
  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 3 "$ramdisk_url" -o "$ART/ramdisk.cpio.gz" && ramdisk_path="$ART/ramdisk.cpio.gz" || true
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$ART/ramdisk.cpio.gz" "$ramdisk_url" && ramdisk_path="$ART/ramdisk.cpio.gz" || true
  fi
fi

# dtb (optional for newer header versions but preferred)
if [[ -z "$dtb_path" && -s "$ART/umi_primary_dtb_paths.txt" ]]; then
  cand="$(head -n1 "$ART/umi_primary_dtb_paths.txt" || true)"
  [[ -f "$cand" ]] && dtb_path="$cand"
fi

# mkbootimg tool detection
if command -v mkbootimg >/dev/null 2>&1; then
  mkbootimg_cmd="mkbootimg"
elif [[ -x "$HOME/.local/bin/mkbootimg" ]]; then
  mkbootimg_cmd="$HOME/.local/bin/mkbootimg"
elif [[ -x "$HOME/.local/bin/mkbootimg.py" ]]; then
  mkbootimg_cmd="$HOME/.local/bin/mkbootimg.py"
elif [[ -f source/tools/mkbootimg/mkbootimg.py ]]; then
  mkbootimg_cmd="python3 source/tools/mkbootimg/mkbootimg.py"
elif [[ -f target/tools/mkbootimg/mkbootimg.py ]]; then
  mkbootimg_cmd="python3 target/tools/mkbootimg/mkbootimg.py"
elif python3 - <<'PY'
import importlib.util
print('ok' if importlib.util.find_spec('mkbootimg') else 'no')
PY
then
  if [[ "$(python3 - <<'PY'
import importlib.util
print('ok' if importlib.util.find_spec('mkbootimg') else 'no')
PY
)" == "ok" ]]; then
    mkbootimg_cmd="python3 -m mkbootimg"
  fi
fi

header_version="${BOOTIMG_HEADER_VERSION:-3}"
base="${BOOTIMG_BASE:-0x00000000}"
pagesize="${BOOTIMG_PAGESIZE:-4096}"
cmdline="${BOOTIMG_CMDLINE:-}"

# fallback: use a prebuilt boot.img directly when mkbootimg inputs are unavailable
if [[ -n "$prebuilt_url" ]]; then
  out_boot="$ART/boot.img"
  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 3 "$prebuilt_url" -o "$out_boot" || true
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$out_boot" "$prebuilt_url" || true
  fi
  if [[ -f "$out_boot" ]]; then
    size="$(stat -c%s "$out_boot" 2>/dev/null || wc -c < "$out_boot")"
    {
      echo "status=ok"
      echo "reason=prebuilt-bootimg-downloaded"
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
      echo "source=prebuilt_url"
      echo "prebuilt_url=$prebuilt_url"
    } > "$OUT"
    echo "bootimg downloaded: $out_boot ($size bytes)"
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
{
  echo "status=ok"
  echo "reason=bootimg-built"
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
} > "$OUT"

echo "bootimg built: $out_boot ($size bytes)"
