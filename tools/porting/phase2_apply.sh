#!/usr/bin/env bash
set -euo pipefail

# Phase 2 minimal bootable porting attempt
# source: SO-TS 4.19 tree
# target: 5+ base tree

SRC_DIR="${1:?source dir required}"
DST_DIR="${2:?target dir required}"
DEVICE="${3:-umi}"

log() { echo "[phase2] $*"; }

PORT_DIR="$DST_DIR/porting/phase2"
mkdir -p "$PORT_DIR"
: > "$PORT_DIR/copied_dts.txt"

# 1) defconfig migration (mandatory)
SRC_DEF="$SRC_DIR/arch/arm64/configs/${DEVICE}_defconfig"
DST_DEF="$DST_DIR/arch/arm64/configs/${DEVICE}_defconfig"

if [[ -f "$SRC_DEF" ]]; then
  log "copy defconfig: $SRC_DEF -> $DST_DEF"
  cp -f "$SRC_DEF" "$DST_DEF"
else
  log "ERROR: source defconfig not found: $SRC_DEF"
  exit 1
fi

# 2) dts/dtsi migration (recursive + path fallback)
# search roots in source
SRC_ROOTS=(
  "arch/arm64/boot/dts/vendor/qcom"
  "arch/arm64/boot/dts/qcom"
)

# destination priority roots (use existing first)
DST_ROOTS=(
  "arch/arm64/boot/dts/qcom"
  "arch/arm64/boot/dts/vendor/qcom"
)

select_dst_root() {
  for r in "${DST_ROOTS[@]}"; do
    if [[ -d "$DST_DIR/$r" ]]; then
      echo "$r"
      return 0
    fi
  done
  # fallback create qcom path
  mkdir -p "$DST_DIR/arch/arm64/boot/dts/qcom"
  echo "arch/arm64/boot/dts/qcom"
}

DST_ROOT="$(select_dst_root)"

copied=0
for rel in "${SRC_ROOTS[@]}"; do
  sroot="$SRC_DIR/$rel"
  if [[ ! -d "$sroot" ]]; then
    continue
  fi

  log "scan DTS recursively in $sroot"
  while IFS= read -r f; do
    b="$(basename "$f")"
    if [[ "$b" =~ umi|sm8250|lmi|cmi|apollo|thyme|alioth ]] && [[ ! "$b" =~ rumi|lumia|sony ]]; then
      # keep relative subtree under chosen target root
      subdir="$(dirname "${f#$sroot/}")"
      [[ "$subdir" == "." ]] && subdir=""
      mkdir -p "$DST_DIR/$DST_ROOT/$subdir"
      cp -f "$f" "$DST_DIR/$DST_ROOT/$subdir/$b"
      echo "$DST_ROOT/$subdir/$b" >> "$PORT_DIR/copied_dts.txt"
      copied=$((copied+1))
    fi
  done < <(find "$sroot" -type f \( -name '*.dts' -o -name '*.dtsi' \))
done

if [[ "$copied" -eq 0 ]]; then
  rm -f "$PORT_DIR/copied_dts.txt"
fi

log "dts copied count: $copied"

# 3) report
{
  echo "device=$DEVICE"
  echo "defconfig=$DST_DEF"
  echo "dst_dts_root=$DST_ROOT"
  echo "dts_copied=$copied"
} > "$PORT_DIR/summary.txt"

log "phase2 apply done"
