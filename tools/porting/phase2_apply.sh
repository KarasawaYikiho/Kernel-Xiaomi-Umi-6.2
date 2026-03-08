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
: > "$PORT_DIR/seed_dts.txt"
: > "$PORT_DIR/included_dts.txt"

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

# 2) dts/dtsi migration (recursive + include-aware)
SRC_ROOTS=(
  "arch/arm64/boot/dts/vendor/qcom"
  "arch/arm64/boot/dts/qcom"
)

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
  mkdir -p "$DST_DIR/arch/arm64/boot/dts/qcom"
  echo "arch/arm64/boot/dts/qcom"
}

DST_ROOT="$(select_dst_root)"

declare -A COPIED

do_copy() {
  local src_file="$1"
  local src_root="$2"

  [[ -f "$src_file" ]] || return 0
  if [[ -n "${COPIED[$src_file]:-}" ]]; then
    return 0
  fi

  local rel subdir base dst_dir dst_file
  rel="${src_file#$src_root/}"
  subdir="$(dirname "$rel")"
  [[ "$subdir" == "." ]] && subdir=""
  base="$(basename "$src_file")"

  dst_dir="$DST_DIR/$DST_ROOT/$subdir"
  mkdir -p "$dst_dir"
  dst_file="$dst_dir/$base"
  cp -f "$src_file" "$dst_file"

  COPIED[$src_file]=1
  echo "$DST_ROOT/$subdir/$base" >> "$PORT_DIR/copied_dts.txt"
}

parse_includes() {
  local f="$1"
  # extract #include "file" or /include/ "file"
  grep -E '^[[:space:]]*(#include|/include/)[[:space:]]+"[^"]+"' "$f" 2>/dev/null \
    | sed -E 's/.*"([^"]+)".*/\1/' || true
}

copy_with_includes() {
  local seed="$1"
  local src_root="$2"

  # BFS queue in plain bash
  local queue_file
  queue_file="$(mktemp)"
  echo "$seed" > "$queue_file"

  while IFS= read -r cur; do
    [[ -f "$cur" ]] || continue
    do_copy "$cur" "$src_root"

    while IFS= read -r inc; do
      [[ -n "$inc" ]] || continue

      # 1) same directory include
      local cand1 cand2
      cand1="$(dirname "$cur")/$inc"
      cand2="$src_root/$inc"

      if [[ -f "$cand1" && -z "${COPIED[$cand1]:-}" ]]; then
        echo "$cand1" >> "$queue_file"
        echo "$inc" >> "$PORT_DIR/included_dts.txt"
      elif [[ -f "$cand2" && -z "${COPIED[$cand2]:-}" ]]; then
        echo "$cand2" >> "$queue_file"
        echo "$inc" >> "$PORT_DIR/included_dts.txt"
      fi
    done < <(parse_includes "$cur")
  done < "$queue_file"

  rm -f "$queue_file"
}

seed_count=0
for rel in "${SRC_ROOTS[@]}"; do
  sroot="$SRC_DIR/$rel"
  [[ -d "$sroot" ]] || continue

  log "scan DTS recursively in $sroot"
  while IFS= read -r f; do
    b="$(basename "$f")"

    # strictly prefer Xiaomi SM8250/UMI family and avoid obvious false positives
    if [[ "$b" =~ (sm8250|umi|xiaomi|kona|lmi|cmi|apollo|alioth|thyme) ]] && [[ ! "$b" =~ (rumi|lumia|sony) ]]; then
      echo "$f" >> "$PORT_DIR/seed_dts.txt"
      copy_with_includes "$f" "$sroot"
      seed_count=$((seed_count+1))
    fi
  done < <(find "$sroot" -type f \( -name '*.dts' -o -name '*.dtsi' \))
done

copied=0
if [[ -s "$PORT_DIR/copied_dts.txt" ]]; then
  copied=$(wc -l < "$PORT_DIR/copied_dts.txt" | tr -d ' ')
fi

if [[ "$copied" -eq 0 ]]; then
  rm -f "$PORT_DIR/copied_dts.txt"
fi

log "seed dts count: $seed_count"
log "dts copied count: $copied"

{
  echo "device=$DEVICE"
  echo "defconfig=$DST_DEF"
  echo "dst_dts_root=$DST_ROOT"
  echo "seed_dts_count=$seed_count"
  echo "dts_copied=$copied"
} > "$PORT_DIR/summary.txt"

log "phase2 apply done"
