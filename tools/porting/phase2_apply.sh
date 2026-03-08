#!/usr/bin/env bash
set -euo pipefail

# Phase 2 minimal bootable porting attempt
# source: SO-TS 4.19 tree
# target: 5+ base tree

SRC_DIR="${1:?source dir required}"
DST_DIR="${2:?target dir required}"
DEVICE="${3:-umi}"

log() { echo "[phase2] $*"; }

mkdir -p "$DST_DIR/porting/phase2"

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

# 2) dts migration candidates (best-effort)
# try common qcom/vendor locations from old tree
CANDIDATE_PATHS=(
  "arch/arm64/boot/dts/vendor/qcom"
  "arch/arm64/boot/dts/qcom"
)

copied=0
for rel in "${CANDIDATE_PATHS[@]}"; do
  s="$SRC_DIR/$rel"
  d="$DST_DIR/$rel"
  if [[ -d "$s" && -d "$d" ]]; then
    log "scan DTS in $s"
    while IFS= read -r f; do
      b="$(basename "$f")"
      if [[ "$b" =~ umi|sm8250|lmi|cmi|apollo|thyme|alioth ]]; then
        cp -f "$f" "$d/$b"
        echo "$rel/$b" >> "$DST_DIR/porting/phase2/copied_dts.txt"
        copied=$((copied+1))
      fi
    done < <(find "$s" -maxdepth 1 -type f \( -name '*.dts' -o -name '*.dtsi' \))
  fi
done

log "dts copied count: $copied"

# 3) simple report
{
  echo "device=$DEVICE"
  echo "defconfig=$DST_DEF"
  echo "dts_copied=$copied"
} > "$DST_DIR/porting/phase2/summary.txt"

log "phase2 apply done"
