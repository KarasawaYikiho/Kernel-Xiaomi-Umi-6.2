#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   Collect_Phase2_Artifacts.sh <device>

DEVICE="${1:-${DEVICE:-unknown}}"

source "Porting/Tools/Common.sh"
initialize_porting_paths
python_cmd="$(require_python_cmd)" || exit 1

BUNDLE_DIR="$ARTIFACTS_DIR/device_bundle"
PRIMARY_DTB_PATHS="$ARTIFACTS_DIR/primary_dtb_paths.txt"
ALL_DTB_PATHS="$ARTIFACTS_DIR/all_dtb_paths.txt"
MANIFEST_PATH="$ARTIFACTS_DIR/target_dtb_manifest.txt"

mkdir -p "$BUNDLE_DIR"
: > "$ALL_DTB_PATHS"
: > "$PRIMARY_DTB_PATHS"
cp -v "$PHASE2_PORT_DIR/summary.txt" "$ARTIFACTS_DIR"/ || true
cp -v "$PHASE2_PORT_DIR/copied_dts.txt" "$ARTIFACTS_DIR"/ || true
cp -v "$PHASE2_PORT_DIR/seed_dts.txt" "$ARTIFACTS_DIR"/ || true
cp -v "$PHASE2_PORT_DIR/included_dts.txt" "$ARTIFACTS_DIR"/ || true
cp -v "$OUT_DIR/.config" "$ARTIFACTS_DIR"/ || true
cp -v "$OUT_DIR/arch/arm64/boot/Image" "$ARTIFACTS_DIR"/ || true
cp -v "$OUT_DIR/arch/arm64/boot/Image.gz" "$ARTIFACTS_DIR"/ || true
cp -v "$OUT_DIR/arch/arm64/boot/boot.img" "$ARTIFACTS_DIR"/ || true
cp -v "$OUT_DIR/boot.img" "$ARTIFACTS_DIR"/ || true

# diagnostic lists
if [ -d "$OUT_DIR/arch/arm64/boot/dts" ]; then
  find "$OUT_DIR/arch/arm64/boot/dts" -type f \( -name '*.dtb' -o -name '*.dtbo' \) > "$ALL_DTB_PATHS" || true
fi

# build manifest from migrated dts list (preferred)
"$python_cmd" Porting/Tools/BuildDtbManifest.py || true

# pick paths by manifest first
if [ -s "$MANIFEST_PATH" ]; then
  while IFS= read -r dtb; do
    [ -n "$dtb" ] || continue
    grep -E "/${dtb}$" "$ALL_DTB_PATHS" >> "$PRIMARY_DTB_PATHS" || true
  done < "$MANIFEST_PATH"
fi

"$python_cmd" Porting/Tools/DtbPostcheck.py || true
"$python_cmd" Porting/Tools/AnalyzeDtbMiss.py || true

# fallback 1: strict umi/xiaomi/sm8250 path matching
if [ ! -s "$PRIMARY_DTB_PATHS" ]; then
  grep -Ei '/.*(sm8250-xiaomi|umi-sm8250|xiaomi-sm8250-common).*(\.dtb|\.dtbo)$' "$ALL_DTB_PATHS" \
    | grep -Eiv 'rumi|lumia|sony' > "$PRIMARY_DTB_PATHS" || true
fi

# fallback 1.5: explicit umi aliases by basename
if [ ! -s "$PRIMARY_DTB_PATHS" ]; then
  grep -Ei '/(sm8250-xiaomi-umi|umi-sm8250|xiaomi-sm8250-common)([^/]*\.(dtb|dtbo))$' "$ALL_DTB_PATHS" \
    | grep -Eiv 'rumi|lumia|sony|hdk|mtp' > "$PRIMARY_DTB_PATHS" || true
fi

# fallback 2: keep it strict to avoid false positives from unrelated boards
if [ ! -s "$PRIMARY_DTB_PATHS" ]; then
  grep -Ei '(sm8250-xiaomi|umi-sm8250|xiaomi-sm8250-common).*(\.dtb|\.dtbo)$' "$ALL_DTB_PATHS" \
    | grep -Eiv 'rumi|lumia|sony|hdk|mtp' > "$PRIMARY_DTB_PATHS" || true
fi

cp -v "$OUT_DIR/arch/arm64/boot/Image" "$BUNDLE_DIR"/ || true
cp -v "$OUT_DIR/arch/arm64/boot/Image.gz" "$BUNDLE_DIR"/ || true
cp -v "$PHASE2_PORT_DIR/summary.txt" "$BUNDLE_DIR"/ || true

dtb_count=0
xiaomi_dtb_count=0
if [ -s "$PRIMARY_DTB_PATHS" ]; then
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    cp -v "$f" "$ARTIFACTS_DIR"/ || true
    cp -v "$f" "$BUNDLE_DIR"/ || true
    dtb_count=$((dtb_count+1))
    echo "$f" | grep -Eiq 'xiaomi|umi|sm8250' && xiaomi_dtb_count=$((xiaomi_dtb_count+1)) || true
  done < "$PRIMARY_DTB_PATHS"
fi

flash_ready="no"
if [ "$xiaomi_dtb_count" -ge 1 ] && [ -f "$OUT_DIR/arch/arm64/boot/Image" ]; then
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
"$python_cmd" Porting/Tools/EvaluateArtifact.py || true
