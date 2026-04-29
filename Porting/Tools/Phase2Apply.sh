#!/usr/bin/env bash
set -euo pipefail

# Phase 2 minimal bootable porting attempt
# source: SO-TS 4.19 reference tree
# target: checked-out yefxx-based kernel tree

SRC_DIR="${1:?source dir required}"
DST_DIR="${2:?target dir required}"
DEVICE="${3:-umi}"

source "Porting/Tools/Common.sh"
initialize_porting_paths
python_cmd="$(require_python_cmd "[phase2] ERROR: python interpreter not found")" || exit 1

log() { echo "[phase2] $*"; }

PORT_DIR="$PHASE2_PORT_DIR"
mkdir -p "$PORT_DIR"
: > "$PORT_DIR/copied_dts.txt"
: > "$PORT_DIR/seed_dts.txt"
: > "$PORT_DIR/included_dts.txt"

# 1) defconfig migration (mandatory)
SRC_DEF="$SRC_DIR/arch/arm64/configs/${DEVICE}_defconfig"
DST_DEF="$DST_DIR/arch/arm64/configs/${DEVICE}_defconfig"

if [[ ! -f "$SRC_DEF" ]]; then
  for cand in "$SRC_DIR/arch/arm64/configs/${DEVICE}_stock-defconfig" "$SRC_DIR/arch/arm64/configs/AOSP_defconfig/${DEVICE}_stock-defconfig"; do
    if [[ -f "$cand" ]]; then
      SRC_DEF="$cand"
      break
    fi
  done
fi

if [[ -f "$SRC_DEF" ]]; then
  log "copy defconfig: $SRC_DEF -> $DST_DEF"
  cp -f "$SRC_DEF" "$DST_DEF"
else
  log "ERROR: source defconfig not found: $SRC_DIR/arch/arm64/configs/${DEVICE}_defconfig"
  exit 1
fi

# defconfig compatibility guards for 5+ target baseline
set_kconfig_n() {
  local cfg="$1"
  sed -i -E "/^${cfg}=.*/d" "$DST_DEF"
  sed -i -E "/^# ${cfg} is not set$/d" "$DST_DEF"
  echo "# ${cfg} is not set" >> "$DST_DEF"
}

# qcom-spmi-adc5 mismatch on current target baseline (undeclared ADC5_* identifiers)
set_kconfig_n "CONFIG_QCOM_SPMI_ADC5"

# DSCP target removed in 6.11 (only xt_dscp.c match exists, not xt_DSCP.c target)
set_kconfig_n "CONFIG_NETFILTER_XT_TARGET_DSCP"

# 1.5) leds color-id compatibility patch (some 5+ bases miss LED_COLOR_ID_* defs)
patch_led_color_compat() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  grep -q "LED_COLOR_ID_MAX" "$f" || return 0

  if ! grep -q "dt-bindings/leds/common.h" "$f"; then
    sed -i '/^#include <linux\/leds.h>/a #include <dt-bindings/leds/common.h>' "$f"
  fi

  if ! grep -q "OC_PHASE2_LED_COLOR_COMPAT" "$f"; then
    "$python_cmd" - "$f" <<'PY'
from pathlib import Path
p = Path(__import__('sys').argv[1])
s = p.read_text(encoding='utf-8', errors='ignore')
needle = '#include <dt-bindings/leds/common.h>\n'
compat = '''\n#ifndef LED_COLOR_ID_MAX\n#define OC_PHASE2_LED_COLOR_COMPAT 1\nenum {\n\tLED_COLOR_ID_WHITE = 0,\n\tLED_COLOR_ID_RED,\n\tLED_COLOR_ID_GREEN,\n\tLED_COLOR_ID_BLUE,\n\tLED_COLOR_ID_AMBER,\n\tLED_COLOR_ID_VIOLET,\n\tLED_COLOR_ID_YELLOW,\n\tLED_COLOR_ID_IR,\n\tLED_COLOR_ID_MULTI,\n\tLED_COLOR_ID_RGB,\n\tLED_COLOR_ID_PURPLE,\n\tLED_COLOR_ID_ORANGE,\n\tLED_COLOR_ID_PINK,\n\tLED_COLOR_ID_CYAN,\n\tLED_COLOR_ID_LIME,\n\tLED_COLOR_ID_MAX,\n};\n#endif\n'''
if needle in s and 'OC_PHASE2_LED_COLOR_COMPAT' not in s:
    s = s.replace(needle, needle + compat, 1)
    p.write_text(s, encoding='utf-8')
PY
  fi
}

patch_led_color_compat "$DST_DIR/drivers/leds/led-core.c"
patch_led_color_compat "$DST_DIR/drivers/leds/led-class.c"

# 1.6) hid apple keyboard backlight LED function compat
HID_APPLE="$DST_DIR/drivers/hid/hid-apple.c"
if [[ -f "$HID_APPLE" ]] && grep -q "LED_FUNCTION_KBD_BACKLIGHT" "$HID_APPLE"; then
  if ! grep -q "OC_PHASE2_LED_FUNCTION_COMPAT" "$HID_APPLE"; then
    "$python_cmd" - "$HID_APPLE" <<'PY'
from pathlib import Path
p = Path(__import__('sys').argv[1])
s = p.read_text(encoding='utf-8', errors='ignore')
if 'OC_PHASE2_LED_FUNCTION_COMPAT' in s:
    raise SystemExit(0)
if '#ifndef LED_FUNCTION_KBD_BACKLIGHT' in s:
    raise SystemExit(0)
needle = '#include <linux/leds.h>\n'
compat = '''#ifndef LED_FUNCTION_KBD_BACKLIGHT
#define OC_PHASE2_LED_FUNCTION_COMPAT 1
#define LED_FUNCTION_KBD_BACKLIGHT "kbd_backlight"
#endif
'''
if needle in s:
    s = s.replace(needle, needle + compat, 1)
else:
    idx = s.find('#include ')
    if idx != -1:
        end = s.find('\n', idx)
        if end != -1:
            s = s[:end+1] + compat + s[end+1:]
        else:
            s = s + '\n' + compat
    else:
        s = compat + '\n' + s
p.write_text(s, encoding='utf-8')
PY
  fi
fi

# 1.7) hid nintendo player LED function compat
HID_NINTENDO="$DST_DIR/drivers/hid/hid-nintendo.c"
if [[ -f "$HID_NINTENDO" ]] && grep -q "LED_FUNCTION_PLAYER1" "$HID_NINTENDO"; then
  if ! grep -q "OC_PHASE2_LED_FUNCTION_PLAYER_COMPAT" "$HID_NINTENDO"; then
    "$python_cmd" - "$HID_NINTENDO" <<'PY'
from pathlib import Path
p = Path(__import__('sys').argv[1])
s = p.read_text(encoding='utf-8', errors='ignore')
if 'OC_PHASE2_LED_FUNCTION_PLAYER_COMPAT' in s:
    raise SystemExit(0)
if '#ifndef LED_FUNCTION_PLAYER1' in s:
    raise SystemExit(0)
needle = '#include <linux/leds.h>\n'
compat = '''#ifndef LED_FUNCTION_PLAYER1
#define OC_PHASE2_LED_FUNCTION_PLAYER_COMPAT 1
#define LED_FUNCTION_PLAYER1 "player-1"
#define LED_FUNCTION_PLAYER2 "player-2"
#define LED_FUNCTION_PLAYER3 "player-3"
#define LED_FUNCTION_PLAYER4 "player-4"
#define LED_FUNCTION_PLAYER5 "player-5"
#endif
'''
if needle in s:
    s = s.replace(needle, needle + compat, 1)
else:
    idx = s.find('#include ')
    if idx != -1:
        end = s.find('\n', idx)
        if end != -1:
            s = s[:end+1] + compat + s[end+1:]
        else:
            s = s + '\n' + compat
    else:
        s = compat + '\n' + s
p.write_text(s, encoding='utf-8')
PY
  fi
fi

# 2) dts/dtsi migration (recursive + include-aware)
SRC_ROOTS=(
  "arch/arm64/boot/dts/vendor/qcom"
  "arch/arm64/boot/dts/vendor/xiaomi"
  "arch/arm64/boot/dts/qcom"
)

select_existing_root() {
  local cand
  for cand in "$@"; do
    if [[ -d "$DST_DIR/$cand" ]]; then
      echo "$cand"
      return 0
    fi
  done
  return 1
}

pick_dst_root_for() {
  local src_rel="$1"
  local picked=""

  case "$src_rel" in
    arch/arm64/boot/dts/vendor/xiaomi)
      picked="$(select_existing_root \
        "arch/arm64/boot/dts/vendor/xiaomi" \
        "arch/arm64/boot/dts/vendor/qcom" \
        "arch/arm64/boot/dts/qcom" || true)"
      [[ -n "$picked" ]] || picked="arch/arm64/boot/dts/vendor/xiaomi"
      ;;
    arch/arm64/boot/dts/vendor/qcom)
      picked="$(select_existing_root \
        "arch/arm64/boot/dts/vendor/qcom" \
        "arch/arm64/boot/dts/qcom" \
        "arch/arm64/boot/dts/vendor/xiaomi" || true)"
      [[ -n "$picked" ]] || picked="arch/arm64/boot/dts/vendor/qcom"
      ;;
    *)
      picked="$(select_existing_root \
        "arch/arm64/boot/dts/qcom" \
        "arch/arm64/boot/dts/vendor/qcom" \
        "arch/arm64/boot/dts/vendor/xiaomi" || true)"
      [[ -n "$picked" ]] || picked="arch/arm64/boot/dts/qcom"
      ;;
  esac

  mkdir -p "$DST_DIR/$picked"
  echo "$picked"
}

declare -A COPIED

do_copy() {
  local src_file="$1"
  local src_root="$2"
  local dst_root="$3"

  [[ -f "$src_file" ]] || return 0
  if [[ -n "${COPIED[$src_file]:-}" ]]; then
    return 0
  fi

  local rel subdir base dst_dir dst_file
  rel="${src_file#$src_root/}"
  subdir="$(dirname "$rel")"
  [[ "$subdir" == "." ]] && subdir=""
  base="$(basename "$src_file")"

  dst_dir="$DST_DIR/$dst_root/$subdir"
  mkdir -p "$dst_dir"
  dst_file="$dst_dir/$base"

  if [[ -f "$dst_file" ]]; then
    COPIED[$src_file]=1
    return 0
  fi

  cp -f "$src_file" "$dst_file"

  COPIED[$src_file]=1
  echo "$dst_root/$subdir/$base" >> "$PORT_DIR/copied_dts.txt"
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
  local dst_root="$3"

  # BFS queue in plain bash
  local queue_file
  queue_file="$(mktemp)"
  echo "$seed" > "$queue_file"

  while IFS= read -r cur; do
    [[ -f "$cur" ]] || continue
    do_copy "$cur" "$src_root" "$dst_root"

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
dst_roots_used=""
for rel in "${SRC_ROOTS[@]}"; do
  sroot="$SRC_DIR/$rel"
  [[ -d "$sroot" ]] || continue
  droot="$(pick_dst_root_for "$rel")"
  case ",$dst_roots_used," in
    *",$droot,"*) ;;
    *) dst_roots_used="${dst_roots_used:+$dst_roots_used,}$droot" ;;
  esac

  log "scan DTS recursively in $sroot -> $droot"
  while IFS= read -r f; do
    b="$(basename "$f")"

    # strictly prefer Xiaomi SM8250/UMI family and avoid obvious false positives
    if [[ "$b" =~ (sm8250|umi|xiaomi|kona|lmi|cmi|apollo|alioth|thyme) ]] && [[ ! "$b" =~ (rumi|lumia|sony|hdk|mtp|pdx|edo) ]]; then
      echo "$f" >> "$PORT_DIR/seed_dts.txt"
      copy_with_includes "$f" "$sroot" "$droot"
      seed_count=$((seed_count+1))
    fi
  done < <(find "$sroot" -type f \( -name '*.dts' -o -name '*.dtsi' \))
done

copied=0
copied_dts=0
copied_dtsi=0
if [[ -s "$PORT_DIR/copied_dts.txt" ]]; then
  copied=$(wc -l < "$PORT_DIR/copied_dts.txt" | tr -d ' ')
  copied_dts=$(grep -Ec '\.dts$' "$PORT_DIR/copied_dts.txt" || true)
  copied_dtsi=$(grep -Ec '\.dtsi$' "$PORT_DIR/copied_dts.txt" || true)
fi

if [[ "$copied" -eq 0 ]]; then
  rm -f "$PORT_DIR/copied_dts.txt"
fi

# 3) dt-bindings header sync (for migrated dts includes)
SRC_BIND="$SRC_DIR/include/dt-bindings"
DST_BIND="$DST_DIR/include/dt-bindings"
bind_copied=0

if [[ -d "$SRC_BIND" ]]; then
  while IFS= read -r h; do
    [[ -f "$h" ]] || continue
    rel="${h#$SRC_BIND/}"
    dst="$DST_BIND/$rel"
    [[ -f "$dst" ]] && continue
    mkdir -p "$(dirname "$dst")"
    cp -f "$h" "$dst"
    bind_copied=$((bind_copied+1))
  done < <(find "$SRC_BIND" -type f -name '*.h')
fi

log "seed dts count: $seed_count"
log "dts/dtsi copied count: $copied (dts=$copied_dts, dtsi=$copied_dtsi)"
log "dt-bindings headers copied: $bind_copied"
log "defconfig guard applied: CONFIG_QCOM_SPMI_ADC5=n"

{
  echo "device=$DEVICE"
  echo "defconfig=$DST_DEF"
  echo "dst_dts_roots=$dst_roots_used"
  echo "seed_dts_count=$seed_count"
  echo "dts_copied=$copied"
  echo "dts_only_copied=$copied_dts"
  echo "dtsi_only_copied=$copied_dtsi"
  echo "dt_bindings_copied=$bind_copied"
} > "$PORT_DIR/summary.txt"

log "phase2 apply done"
