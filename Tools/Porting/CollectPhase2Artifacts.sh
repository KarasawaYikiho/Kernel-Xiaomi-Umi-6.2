#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   Collect_Phase2_Artifacts.sh <device>

DEVICE="${1:-${DEVICE:-unknown}}"
BUNDLE_DIR="artifacts/device_bundle"
PRIMARY_DTB_PATHS="artifacts/primary_dtb_paths.txt"

source "Tools/Porting/Common.sh"
python_cmd="$(require_python_cmd)" || exit 1

mkdir -p "$BUNDLE_DIR"
: > artifacts/all_dtb_paths.txt
: > "$PRIMARY_DTB_PATHS"
cp -v target/Porting/phase2/summary.txt artifacts/ || true
cp -v target/Porting/phase2/copied_dts.txt artifacts/ || true
cp -v target/Porting/phase2/seed_dts.txt artifacts/ || true
cp -v target/Porting/phase2/included_dts.txt artifacts/ || true
cp -v out/.config artifacts/ || true
cp -v out/arch/arm64/boot/Image artifacts/ || true
cp -v out/arch/arm64/boot/Image.gz artifacts/ || true
cp -v out/arch/arm64/boot/boot.img artifacts/ || true
cp -v out/boot.img artifacts/ || true

# diagnostic lists
if [ -d out/arch/arm64/boot/dts ]; then
  find out/arch/arm64/boot/dts -type f \( -name '*.dtb' -o -name '*.dtbo' \) > artifacts/all_dtb_paths.txt || true
fi

# build manifest from migrated dts list (preferred)
"$python_cmd" Tools/Porting/BuildDtbManifest.py || true

# pick paths by manifest first
if [ -s artifacts/target_dtb_manifest.txt ]; then
  while IFS= read -r dtb; do
    [ -n "$dtb" ] || continue
    grep -E "/${dtb}$" artifacts/all_dtb_paths.txt >> "$PRIMARY_DTB_PATHS" || true
  done < artifacts/target_dtb_manifest.txt
fi

"$python_cmd" Tools/Porting/DtbPostcheck.py || true
"$python_cmd" Tools/Porting/AnalyzeDtbMiss.py || true

# fallback 1: strict umi/xiaomi/sm8250 path matching
if [ ! -s "$PRIMARY_DTB_PATHS" ]; then
  grep -Ei '/.*(sm8250-xiaomi|umi-sm8250|xiaomi-sm8250-common).*(\.dtb|\.dtbo)$' artifacts/all_dtb_paths.txt \
    | grep -Eiv 'rumi|lumia|sony' > "$PRIMARY_DTB_PATHS" || true
fi

# fallback 1.5: explicit umi aliases by basename
if [ ! -s "$PRIMARY_DTB_PATHS" ]; then
  grep -Ei '/(sm8250-xiaomi-umi|umi-sm8250|xiaomi-sm8250-common)([^/]*\.(dtb|dtbo))$' artifacts/all_dtb_paths.txt \
    | grep -Eiv 'rumi|lumia|sony|hdk|mtp' > "$PRIMARY_DTB_PATHS" || true
fi

# fallback 2: keep it strict to avoid false positives from unrelated boards
if [ ! -s "$PRIMARY_DTB_PATHS" ]; then
  grep -Ei '(sm8250-xiaomi|umi-sm8250|xiaomi-sm8250-common).*(\.dtb|\.dtbo)$' artifacts/all_dtb_paths.txt \
    | grep -Eiv 'rumi|lumia|sony|hdk|mtp' > "$PRIMARY_DTB_PATHS" || true
fi

cp -v out/arch/arm64/boot/Image "$BUNDLE_DIR"/ || true
cp -v out/arch/arm64/boot/Image.gz "$BUNDLE_DIR"/ || true
cp -v target/Porting/phase2/summary.txt "$BUNDLE_DIR"/ || true

dtb_count=0
xiaomi_dtb_count=0
if [ -s "$PRIMARY_DTB_PATHS" ]; then
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    cp -v "$f" artifacts/ || true
    cp -v "$f" "$BUNDLE_DIR"/ || true
    dtb_count=$((dtb_count+1))
    echo "$f" | grep -Eiq 'xiaomi|umi|sm8250' && xiaomi_dtb_count=$((xiaomi_dtb_count+1)) || true
  done < "$PRIMARY_DTB_PATHS"
fi

flash_ready="no"
if [ "$xiaomi_dtb_count" -ge 1 ] && [ -f out/arch/arm64/boot/Image ]; then
  flash_ready="candidate"
fi

{
  echo "device=$DEVICE"
  echo "bundle_dtb_count=$dtb_count"
  echo "bundle_xiaomi_dtb_count=$xiaomi_dtb_count"
  echo "flash_ready_hint=$flash_ready"
} > "$BUNDLE_DIR"/pack-info.txt

if command -v zip >/dev/null 2>&1; then
  (cd "$BUNDLE_DIR" && zip -r ../phase2-device-package.zip .) || true
fi
"$python_cmd" Tools/Porting/EvaluateArtifact.py || true
