#!/usr/bin/env bash
set -euo pipefail

# Best-effort release boot.img preparation.
# Requires kernel image + ramdisk + mkbootimg parameters.
# Writes artifacts/bootimg-build.txt with explicit blockers when inputs are missing.

source "Porting/Tools/Common.sh"
initialize_porting_paths

ART="$ARTIFACTS_DIR"
mkdir -p "$ART"
OUT="$ART/bootimg-build.txt"
DEFAULT_OFFICIAL_ROM_ZIP=''
DEFAULT_OFFICIAL_ROM_DIR=''
ROM_ANALYSIS='Porting/OfficialRomAnalysis.md'
ROM_BASELINE_ENV='Porting/OfficialRomBaseline/BootImageBaseline.env'
ROM_BASELINE_DIR='Porting/OfficialRomBaseline'

kernel_path=""
ramdisk_path="${BOOTIMG_RAMDISK_PATH:-}"
prebuilt_path="${BOOTIMG_PREBUILT_PATH:-}"
dtb_path="${BOOTIMG_DTB_PATH:-}"
mkbootimg_cmd=""
official_rom_zip="${OFFICIAL_ROM_ZIP:-}"
official_bootimg_path="${OFFICIAL_BOOTIMG_PATH:-}"
official_rom_dir="${OFFICIAL_ROM_DIR:-}"
python_cmd=""
rom_source_used=""
rom_baseline_bootimg_path=""
materialized_bootimg_path=""

load_port_defaults() {
  local config_lines
  config_lines="$(python_cmd="$(resolve_python_cmd || true)"; if [[ -n "$python_cmd" ]]; then "$python_cmd" Porting/Tools/ExportPortConfig.py 2>/dev/null; fi)"
  [[ -n "$config_lines" ]] || return 0
  while IFS='=' read -r key value; do
    case "$key" in
      OFFICIAL_ROM_DIR_DEFAULT)
        [[ -n "$value" ]] && DEFAULT_OFFICIAL_ROM_DIR="$value"
        ;;
      OFFICIAL_ROM_ZIP_DEFAULT)
        [[ -n "$value" ]] && DEFAULT_OFFICIAL_ROM_ZIP="$value"
        ;;
      OFFICIAL_ROM_BASELINE_DIR)
        [[ -n "$value" ]] && ROM_BASELINE_DIR="$value"
        ;;
      OFFICIAL_ROM_ENV)
        [[ -n "$value" ]] && ROM_BASELINE_ENV="$value"
        ;;
    esac
  done <<< "$config_lines"
}

load_port_defaults

if [[ -z "$official_rom_zip" ]]; then
  official_rom_zip="$DEFAULT_OFFICIAL_ROM_ZIP"
fi
if [[ -z "$official_rom_dir" ]]; then
  official_rom_dir="$DEFAULT_OFFICIAL_ROM_DIR"
fi

normalize_input_path() {
  local value="$1"
  local drive rest candidate_mnt candidate_drive
  [[ -n "$value" ]] || return 0
  if [[ "$value" =~ ^[A-Za-z]:[\\/].* ]]; then
    if command -v cygpath >/dev/null 2>&1; then
      cygpath -u "$value" 2>/dev/null && return 0
    fi
    drive="${value:0:1}"
    rest="${value:2}"
    rest="${rest//\\//}"
    candidate_mnt="/mnt/${drive,,}${rest}"
    candidate_drive="/${drive,,}${rest}"
    if [[ -e "$candidate_mnt" || -d "$candidate_mnt" ]]; then
      printf '%s\n' "$candidate_mnt"
      return 0
    fi
    if [[ -e "$candidate_drive" || -d "$candidate_drive" ]]; then
      printf '%s\n' "$candidate_drive"
      return 0
    fi
    printf '%s\n' "$candidate_mnt"
    return 0
  fi
  printf '%s\n' "$value"
}

ramdisk_path="$(normalize_input_path "$ramdisk_path")"
prebuilt_path="$(normalize_input_path "$prebuilt_path")"
dtb_path="$(normalize_input_path "$dtb_path")"
official_rom_zip="$(normalize_input_path "$official_rom_zip")"
official_bootimg_path="$(normalize_input_path "$official_bootimg_path")"
official_rom_dir="$(normalize_input_path "$official_rom_dir")"

is_android_boot_image() {
  local path="$1"
  [[ -f "$path" ]] || return 1
  local magic
  magic="$(dd if="$path" bs=8 count=1 2>/dev/null | tr -d '\0' || true)"
  [[ "$magic" == "ANDROID!" ]]
}

is_zip_file() {
  local path="$1"
  [[ -f "$path" ]] || return 1
  local sig
  sig="$(dd if="$path" bs=4 count=1 2>/dev/null | xxd -p -c 4 || true)"
  [[ "$sig" == "504b0304" || "$sig" == "504b0506" || "$sig" == "504b0708" ]]
}

detect_python() {
  python_cmd="$(resolve_python_cmd || true)"
  [[ -n "$python_cmd" ]]
}

resolve_mkbootimg() {
  detect_python || true

  if command -v mkbootimg >/dev/null 2>&1; then
    mkbootimg_cmd="mkbootimg"
  elif [[ -x "$HOME/.local/bin/mkbootimg" ]]; then
    mkbootimg_cmd="$HOME/.local/bin/mkbootimg"
  elif [[ -x "$HOME/.local/bin/mkbootimg.py" ]]; then
    mkbootimg_cmd="$HOME/.local/bin/mkbootimg.py"
  elif [[ -n "$python_cmd" && -f "$REFERENCE_DIR/Tools/mkbootimg/mkbootimg.py" ]]; then
    mkbootimg_cmd="$python_cmd $REFERENCE_DIR/Tools/mkbootimg/mkbootimg.py"
  elif [[ -n "$python_cmd" && -f "$KERNEL_DIR/Tools/mkbootimg/mkbootimg.py" ]]; then
    mkbootimg_cmd="$python_cmd $KERNEL_DIR/Tools/mkbootimg/mkbootimg.py"
  elif [[ -n "$python_cmd" && -f "$KERNEL_DIR/tools/mkbootimg/mkbootimg.py" ]]; then
    mkbootimg_cmd="$python_cmd $KERNEL_DIR/tools/mkbootimg/mkbootimg.py"
  elif [[ -n "$python_cmd" ]]; then
    py_mkbootimg="$($python_cmd - <<'PY'
import importlib.util
print('ok' if importlib.util.find_spec('mkbootimg') else 'no')
PY
)"
    if [[ "$py_mkbootimg" == "ok" ]]; then
      mkbootimg_cmd="$python_cmd -m mkbootimg"
    fi
  fi

}

read_rom_analysis_value() {
  local key="$1"
  [[ -f "$ROM_ANALYSIS" ]] || return 1
  if [[ -n "$python_cmd" ]]; then
    "$python_cmd" - "$ROM_ANALYSIS" "$key" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
key = sys.argv[2]
text = path.read_text(encoding='utf-8', errors='ignore')

patterns = {
    'boot_size': r"`boot\.img`: size=`(\d+)`",
    'boot_sha256': r"`boot\.img`: size=`\d+` sha256=`([0-9a-f]{64})`",
    'header_version_guess': r"header_version_guess \(legacy offset\): `(\d+)`",
}
pat = patterns.get(key)
if not pat:
    raise SystemExit(1)
m = re.search(pat, text, re.IGNORECASE)
if m:
    print(m.group(1))
PY
    return 0
  fi
  return 1
}

read_baseline_env_value() {
  local key="$1"
  [[ -f "$ROM_BASELINE_ENV" ]] || return 1
  if [[ -n "$python_cmd" ]]; then
    "$python_cmd" - "$ROM_BASELINE_ENV" "$key" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
key = sys.argv[2].strip()
for raw in path.read_text(encoding='utf-8', errors='ignore').splitlines():
    line = raw.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    if k.strip() == key:
        print(v.strip())
        break
PY
    return 0
  fi
  return 1
}

extract_bootimg_from_zip() {
  local zip_path="$1"
  local out_path="$2"
  local tmp_path="$3"
  [[ -f "$zip_path" ]] || return 1
  command -v unzip >/dev/null 2>&1 || return 1
  rm -f "$tmp_path"
  unzip -p "$zip_path" "*boot.img" > "$tmp_path" 2>/dev/null || return 1
  if is_android_boot_image "$tmp_path"; then
    mv -f "$tmp_path" "$out_path"
    return 0
  fi
  rm -f "$tmp_path"
  return 1
}

extract_named_from_zip() {
  local zip_path="$1"
  local entry_name="$2"
  local out_path="$3"
  local tmp_path="$4"
  [[ -f "$zip_path" ]] || return 1
  rm -f "$tmp_path"
  if command -v unzip >/dev/null 2>&1; then
    unzip -p "$zip_path" "$entry_name" > "$tmp_path" 2>/dev/null || return 1
  elif [[ -n "$python_cmd" ]]; then
    "$python_cmd" - "$zip_path" "$entry_name" "$tmp_path" <<'PY'
import sys
import zipfile

zip_path, entry_name, out_path = sys.argv[1:4]
with zipfile.ZipFile(zip_path) as zf:
    data = zf.read(entry_name)
with open(out_path, 'wb') as f:
    f.write(data)
PY
  else
    return 1
  fi
  if [[ -s "$tmp_path" ]]; then
    mv -f "$tmp_path" "$out_path"
    return 0
  fi
  rm -f "$tmp_path"
  return 1
}

extract_rom_support_images() {
  local rom_ref="$1"
  local tmp_dtbo="$ART/rom-dtbo.tmp"
  local tmp_vbmeta="$ART/rom-vbmeta.tmp"
  local tmp_vbmeta_system="$ART/rom-vbmeta-system.tmp"
  if [[ -d "$rom_ref" ]]; then
    if [[ -f "$rom_ref/Dtbo.img" ]]; then
      cp -f "$rom_ref/Dtbo.img" "$ART/dtbo.img"
    elif [[ -f "$rom_ref/dtbo.img" ]]; then
      cp -f "$rom_ref/dtbo.img" "$ART/dtbo.img"
    elif [[ -f "$rom_ref/firmware-update/dtbo.img" ]]; then
      cp -f "$rom_ref/firmware-update/dtbo.img" "$ART/dtbo.img"
    fi
    if [[ -f "$rom_ref/Vbmeta.img" ]]; then
      cp -f "$rom_ref/Vbmeta.img" "$ART/vbmeta.img"
    elif [[ -f "$rom_ref/vbmeta.img" ]]; then
      cp -f "$rom_ref/vbmeta.img" "$ART/vbmeta.img"
    elif [[ -f "$rom_ref/firmware-update/vbmeta.img" ]]; then
      cp -f "$rom_ref/firmware-update/vbmeta.img" "$ART/vbmeta.img"
    fi
    if [[ -f "$rom_ref/Vbmeta-System.img" ]]; then
      cp -f "$rom_ref/Vbmeta-System.img" "$ART/vbmeta_system.img"
    elif [[ -f "$rom_ref/vbmeta_system.img" ]]; then
      cp -f "$rom_ref/vbmeta_system.img" "$ART/vbmeta_system.img"
    elif [[ -f "$rom_ref/firmware-update/vbmeta_system.img" ]]; then
      cp -f "$rom_ref/firmware-update/vbmeta_system.img" "$ART/vbmeta_system.img"
    fi
    return 0
  fi
  is_zip_file "$rom_ref" || return 0
  extract_named_from_zip "$rom_ref" "firmware-update/dtbo.img" "$ART/dtbo.img" "$tmp_dtbo" || true
  extract_named_from_zip "$rom_ref" "firmware-update/vbmeta.img" "$ART/vbmeta.img" "$tmp_vbmeta" || true
  extract_named_from_zip "$rom_ref" "firmware-update/vbmeta_system.img" "$ART/vbmeta_system.img" "$tmp_vbmeta_system" || true
}

write_bootimg_ok() {
  local reason="$1"
  local source_name="$2"
  local source_ref="$3"
  local out_boot="$4"
  local size="$5"
  {
    echo "status=ok"
    echo "reason=$reason"
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
    echo "source=$source_name"
    echo "source_ref=$source_ref"
    echo "official_bootimg_path=$official_bootimg_path"
  } > "$OUT"
}

prepare_prebuilt_bootimg() {
  local in_path="$1"
  local source_name="$2"
  local source_ref="$3"
  local out_boot="$ART/boot.img"
  local tmp_boot="$ART/prebuilt-boot.img"
  local size final_reason

  rm -f "$out_boot" "$tmp_boot"
  if is_android_boot_image "$in_path"; then
    cp -f "$in_path" "$out_boot"
  elif is_zip_file "$in_path"; then
    extract_bootimg_from_zip "$in_path" "$out_boot" "$tmp_boot" || true
  fi

  if [[ -f "$out_boot" ]] && is_android_boot_image "$out_boot"; then
    size="$(stat -c%s "$out_boot" 2>/dev/null || wc -c < "$out_boot")"
    final_reason="${source_name}-bootimg-ready"
    if [[ "$required_bytes" =~ ^[0-9]+$ ]] && [[ "$required_bytes" -gt 0 ]]; then
      if [[ "$size" -lt "$required_bytes" ]]; then
        truncate -s "$required_bytes" "$out_boot"
        size="$required_bytes"
        final_reason="${source_name}-bootimg-padded-to-rom-size"
      elif [[ "$size" -gt "$required_bytes" ]]; then
        final_reason="${source_name}-bootimg-oversize"
      fi
    fi
    write_bootimg_ok "$final_reason" "$source_name" "$source_ref" "$out_boot" "$size"
    echo "bootimg prepared: $out_boot ($size bytes)"
    exit 0
  fi
}

prepare_official_rom_bootimg() {
  local out_boot="$ART/boot.img"
  local tmp_boot="$ART/official-rom-boot.tmp"
  local source_boot="$ART/official-rom-boot-source.img"

  rm -f "$out_boot" "$tmp_boot" "$source_boot"
  if [[ -n "$official_bootimg_path" && -f "$official_bootimg_path" ]]; then
    cp -f "$official_bootimg_path" "$source_boot"
  elif [[ -n "$rom_baseline_bootimg_path" && -f "$rom_baseline_bootimg_path" ]]; then
    cp -f "$rom_baseline_bootimg_path" "$source_boot"
  elif [[ -n "$official_rom_zip" && -f "$official_rom_zip" ]]; then
    extract_bootimg_from_zip "$official_rom_zip" "$source_boot" "$tmp_boot" || true
  fi

  if [[ -f "$source_boot" ]] && is_android_boot_image "$source_boot"; then
    prepare_prebuilt_bootimg "$source_boot" "official_rom_baseline" "$rom_source_used"
  fi
}

# kernel
if [[ -f "$OUT_DIR/arch/arm64/boot/Image.gz" ]]; then
  kernel_path="$OUT_DIR/arch/arm64/boot/Image.gz"
elif [[ -f "$OUT_DIR/arch/arm64/boot/Image" ]]; then
  kernel_path="$OUT_DIR/arch/arm64/boot/Image"
fi

# ramdisk (mandatory for direct flashable boot.img)
if [[ -z "$ramdisk_path" ]]; then
  for p in \
    "$ART/ramdisk.cpio.gz" \
    "$KERNEL_DIR/ramdisk.cpio.gz" \
    "$KERNEL_DIR/boot/ramdisk.cpio.gz"; do
    [[ -f "$p" ]] && ramdisk_path="$p" && break
  done
fi

if [[ -n "$ramdisk_path" && -f "$ramdisk_path" ]] && is_zip_file "$ramdisk_path"; then
  extracted_ramdisk="$ART/ramdisk.cpio.gz"
  rm -f "$extracted_ramdisk"
  if command -v unzip >/dev/null 2>&1; then
    if unzip -p "$ramdisk_path" "*ramdisk*.cpio.gz" > "$extracted_ramdisk" 2>/dev/null; then
      ramdisk_path="$extracted_ramdisk"
    elif unzip -p "$ramdisk_path" "*initramfs*.cpio.gz" > "$extracted_ramdisk" 2>/dev/null; then
      ramdisk_path="$extracted_ramdisk"
    else
      ramdisk_path=""
    fi
  else
    ramdisk_path=""
  fi
fi

# dtb (optional for newer header versions but preferred)
if [[ -z "$dtb_path" && -s "$ART/primary_dtb_paths.txt" ]]; then
  cand="$(head -n1 "$ART/primary_dtb_paths.txt" || true)"
  [[ -f "$cand" ]] && dtb_path="$cand"
fi

detect_python || true

if [[ -f "$ROM_BASELINE_DIR/boot.img" ]]; then
  rom_baseline_bootimg_path="$ROM_BASELINE_DIR/boot.img"
fi

if [[ -f "$official_rom_zip" ]]; then
  rom_source_used="$official_rom_zip"
  official_bootimg_path=""
elif [[ -n "$official_bootimg_path" && -f "$official_bootimg_path" ]]; then
  rom_source_used="$official_bootimg_path"
elif [[ -f "$official_rom_dir/boot.img" ]]; then
  rom_source_used="$official_rom_dir"
  official_bootimg_path="$official_rom_dir/boot.img"
elif [[ -n "$rom_baseline_bootimg_path" ]]; then
  rom_source_used="$ROM_BASELINE_DIR"
fi

baseline_header_version="$(read_baseline_env_value BOOTIMG_HEADER_VERSION 2>/dev/null || true)"
baseline_boot_size="$(read_baseline_env_value BOOTIMG_REQUIRED_BYTES 2>/dev/null || true)"
baseline_base="$(read_baseline_env_value BOOTIMG_BASE 2>/dev/null || true)"
baseline_pagesize="$(read_baseline_env_value BOOTIMG_PAGESIZE 2>/dev/null || true)"
rom_baseline_bootimg_path="$(read_baseline_env_value ROM_BOOTIMG_PATH 2>/dev/null || true)"
rom_baseline_bootimg_path="$(normalize_input_path "$rom_baseline_bootimg_path")"

if [[ -z "$rom_baseline_bootimg_path" && -n "$python_cmd" && -f Porting/Tools/MaterializeOfficialBootimg.py ]]; then
  materialized_bootimg_path="$($python_cmd Porting/Tools/MaterializeOfficialBootimg.py 2>/dev/null || true)"
  materialized_bootimg_path="$(normalize_input_path "$materialized_bootimg_path")"
  if [[ -n "$materialized_bootimg_path" && -f "$materialized_bootimg_path" ]]; then
    rom_baseline_bootimg_path="$materialized_bootimg_path"
  fi
fi

if [[ -z "$rom_source_used" && -n "$rom_baseline_bootimg_path" && -f "$rom_baseline_bootimg_path" ]]; then
  rom_source_used="$rom_baseline_bootimg_path"
fi

rom_header_version="$(read_rom_analysis_value header_version_guess 2>/dev/null || true)"
rom_boot_size="$(read_rom_analysis_value boot_size 2>/dev/null || true)"

header_version="${BOOTIMG_HEADER_VERSION:-${baseline_header_version:-${rom_header_version:-3}}}"
base="${BOOTIMG_BASE:-${baseline_base:-0x00000000}}"
pagesize="${BOOTIMG_PAGESIZE:-${baseline_pagesize:-4096}}"
cmdline="${BOOTIMG_CMDLINE:-}"
required_bytes="${BOOTIMG_REQUIRED_BYTES:-${baseline_boot_size:-${rom_boot_size:-134217728}}}"

# Preferred ROM-aligned fallback order:
# 1. Local official ROM package or extracted ROM directory
# 2. Local repository-side boot baseline when manually present outside git
# 3. Local boot baseline path pinned in BootImageBaseline.env
if [[ -n "$rom_source_used" ]]; then
  extract_rom_support_images "$rom_source_used"
  prepare_official_rom_bootimg
fi

# fallback: use a prebuilt boot.img directly when mkbootimg inputs are unavailable
if [[ -n "$prebuilt_path" && -f "$prebuilt_path" ]]; then
  prepare_prebuilt_bootimg "$prebuilt_path" "prebuilt_path" "$prebuilt_path"
fi

resolve_mkbootimg

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
    echo "baseline_bootimg_path=$rom_baseline_bootimg_path"
  } > "$OUT"
  echo "bootimg build blocked: $(IFS=,; echo "${missing[*]}")"
  exit 0
fi

# build boot.img into artifacts
out_boot="$ART/boot.img"
mkbootimg_args=(
  --kernel "$kernel_path"
  --ramdisk "$ramdisk_path"
  --header_version "$header_version"
  --base "$base"
  --pagesize "$pagesize"
  --cmdline "$cmdline"
  --output "$out_boot"
)
if [[ -n "$dtb_path" && -f "$dtb_path" ]]; then
  mkbootimg_args+=(--dtb "$dtb_path")
fi

set +e
if [[ "$mkbootimg_cmd" == *" -m mkbootimg" ]]; then
  "$python_cmd" -m mkbootimg "${mkbootimg_args[@]}"
  rc=$?
elif [[ -n "$python_cmd" && "$mkbootimg_cmd" == "$python_cmd "* ]]; then
  mkbootimg_py="${mkbootimg_cmd#$python_cmd }"
  "$python_cmd" "$mkbootimg_py" "${mkbootimg_args[@]}"
  rc=$?
else
  "$mkbootimg_cmd" "${mkbootimg_args[@]}"
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
  echo "source=mkbootimg"
  echo "source_ref=$mkbootimg_cmd"
} > "$OUT"

echo "bootimg built: $out_boot ($size bytes)"
