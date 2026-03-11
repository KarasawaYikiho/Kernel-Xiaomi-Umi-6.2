#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   Collect_Phase2_Artifacts.sh <device>

DEVICE="${1:-umi}"

mkdir -p artifacts/umi_bundle
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
find out/arch/arm64/boot/dts -type f \( -name '*.dtb' -o -name '*.dtbo' \) > artifacts/all_dtb_paths.txt || true

# build manifest from migrated dts list (preferred)
python3 Tools/Porting/Build_Dtb_Manifest.py || true

# pick paths by manifest first
: > artifacts/umi_primary_dtb_paths.txt
if [ -s artifacts/target_dtb_manifest.txt ]; then
  while IFS= read -r dtb; do
    [ -n "$dtb" ] || continue
    grep -E "/${dtb}$" artifacts/all_dtb_paths.txt >> artifacts/umi_primary_dtb_paths.txt || true
  done < artifacts/target_dtb_manifest.txt
fi

python3 Tools/Porting/Dtb_Postcheck.py || true
python3 Tools/Porting/Analyze_Dtb_Miss.py || true

# fallback 1: strict umi/xiaomi/sm8250 path matching
if [ ! -s artifacts/umi_primary_dtb_paths.txt ]; then
  grep -Ei '/.*(sm8250-xiaomi|umi-sm8250|xiaomi-sm8250-common).*(\.dtb|\.dtbo)$' artifacts/all_dtb_paths.txt \
    | grep -Eiv 'rumi|lumia|sony' > artifacts/umi_primary_dtb_paths.txt || true
fi

# fallback 2: keep it strict to avoid false positives from unrelated boards
if [ ! -s artifacts/umi_primary_dtb_paths.txt ]; then
  grep -Ei '(sm8250-xiaomi|umi-sm8250|xiaomi-sm8250-common).*(\.dtb|\.dtbo)$' artifacts/all_dtb_paths.txt \
    | grep -Eiv 'rumi|lumia|sony|hdk|mtp' > artifacts/umi_primary_dtb_paths.txt || true
fi

cp -v out/arch/arm64/boot/Image artifacts/umi_bundle/ || true
cp -v out/arch/arm64/boot/Image.gz artifacts/umi_bundle/ || true
cp -v target/Porting/phase2/summary.txt artifacts/umi_bundle/ || true

dtb_count=0
xiaomi_dtb_count=0
if [ -s artifacts/umi_primary_dtb_paths.txt ]; then
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    cp -v "$f" artifacts/ || true
    cp -v "$f" artifacts/umi_bundle/ || true
    dtb_count=$((dtb_count+1))
    echo "$f" | grep -Eiq 'xiaomi|umi|sm8250' && xiaomi_dtb_count=$((xiaomi_dtb_count+1)) || true
  done < artifacts/umi_primary_dtb_paths.txt
fi

flash_ready="no"
if [ "$xiaomi_dtb_count" -ge 1 ] && [ -f out/arch/arm64/boot/Image ]; then
  flash_ready="candidate"
fi

{
  echo "device=$DEVICE"
  echo "umi_bundle_dtb_count=$dtb_count"
  echo "umi_bundle_xiaomi_dtb_count=$xiaomi_dtb_count"
  echo "flash_ready_hint=$flash_ready"
} > artifacts/umi_bundle/pack-info.txt

(cd artifacts/umi_bundle && zip -r ../phase2-umi-focused-package.zip .)
python3 Tools/Porting/Evaluate_Artifact.py || true
