#!/usr/bin/env bash
set -euo pipefail

# Best-effort release boot.img preparation.
# Requires kernel image + ramdisk + mkbootimg parameters.
# Writes artifacts/bootimg-build.txt with explicit blockers when inputs are missing.

ART=artifacts
mkdir -p "$ART"
OUT="$ART/bootimg-build.txt"
DEFAULT_OFFICIAL_ROM_ZIP='D:\GIT\MIUI_UMI_OS1.0.5.0.TJBCNXM_d01651ed86_13.0.zip'
DEFAULT_OFFICIAL_ROM_DIR='D:\GIT\MIUI_UMI'
ROM_ANALYSIS='Porting/OfficialRomAnalysis.md'
ROM_BASELINE_ENV='Porting/OfficialRomBaseline/BootImageBaseline.env'
ROM_BASELINE_DIR='Porting/OfficialRomBaseline'

kernel_path=""
ramdisk_path="${BOOTIMG_RAMDISK_PATH:-}"
ramdisk_url="${BOOTIMG_RAMDISK_URL:-}"
prebuilt_url="${BOOTIMG_PREBUILT_URL:-}"
dtb_path="${BOOTIMG_DTB_PATH:-}"
mkbootimg_cmd=""
official_rom_zip="${OFFICIAL_ROM_ZIP:-$DEFAULT_OFFICIAL_ROM_ZIP}"
official_rom_dir="${OFFICIAL_ROM_DIR:-$DEFAULT_OFFICIAL_ROM_DIR}"
python_cmd=""
official_bootimg_path=""
rom_source_used=""
rom_baseline_bootimg_path=""
rom_baseline_bootimg_url=""

source "Tools/Porting/Common.sh"

fetch_file() {
  local url="$1"; local out="$2"
  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 3 "$url" -o "$out" && return 0
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$out" "$url" && return 0
  fi
  return 1
}

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
  elif [[ -n "$python_cmd" && -f source/Tools/mkbootimg/mkbootimg.py ]]; then
    mkbootimg_cmd="$python_cmd source/Tools/mkbootimg/mkbootimg.py"
  elif [[ -n "$python_cmd" && -f target/Tools/mkbootimg/mkbootimg.py ]]; then
    mkbootimg_cmd="$python_cmd target/Tools/mkbootimg/mkbootimg.py"
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

  if [[ -z "$mkbootimg_cmd" && -n "$python_cmd" ]]; then
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
        mkbootimg_cmd="$python_cmd $fetched"
        break
      fi
    done
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
    if [[ -f "$rom_ref/dtbo.img" ]]; then
      cp -f "$rom_ref/dtbo.img" "$ART/dtbo.img"
    elif [[ -f "$rom_ref/firmware-update/dtbo.img" ]]; then
      cp -f "$rom_ref/firmware-update/dtbo.img" "$ART/dtbo.img"
    fi
    if [[ -f "$rom_ref/vbmeta.img" ]]; then
      cp -f "$rom_ref/vbmeta.img" "$ART/vbmeta.img"
    elif [[ -f "$rom_ref/firmware-update/vbmeta.img" ]]; then
      cp -f "$rom_ref/firmware-update/vbmeta.img" "$ART/vbmeta.img"
    fi
    if [[ -f "$rom_ref/vbmeta_system.img" ]]; then
      cp -f "$rom_ref/vbmeta_system.img" "$ART/vbmeta_system.img"
    elif [[ -f "$rom_ref/firmware-update/vbmeta_system.img" ]]; then
      cp -f "$rom_ref/firmware-update/vbmeta_system.img" "$ART/vbmeta_system.img"
    fi
    return 0
  fi
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

detect_python || true

if [[ -f "$ROM_BASELINE_DIR/boot.img" ]]; then
  rom_baseline_bootimg_path="$ROM_BASELINE_DIR/boot.img"
fi

if [[ -n "$official_rom_zip" && "$official_rom_zip" == *"://"* ]]; then
  official_rom_dl="$ART/official-rom-download.zip"
  if fetch_file "$official_rom_zip" "$official_rom_dl"; then
    official_rom_zip="$official_rom_dl"
  fi
fi

if [[ -f "$official_rom_zip" ]]; then
  rom_source_used="$official_rom_zip"
  official_bootimg_path=""
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
rom_baseline_bootimg_url="$(read_baseline_env_value ROM_BOOTIMG_URL 2>/dev/null || true)"

if [[ -z "$rom_source_used" && -n "$rom_baseline_bootimg_url" ]]; then
  rom_source_used="$rom_baseline_bootimg_url"
fi

rom_header_version="$(read_rom_analysis_value header_version_guess 2>/dev/null || true)"
rom_boot_size="$(read_rom_analysis_value boot_size 2>/dev/null || true)"

header_version="${BOOTIMG_HEADER_VERSION:-${baseline_header_version:-${rom_header_version:-3}}}"
base="${BOOTIMG_BASE:-${baseline_base:-0x00000000}}"
pagesize="${BOOTIMG_PAGESIZE:-${baseline_pagesize:-4096}}"
cmdline="${BOOTIMG_CMDLINE:-}"
required_bytes="${BOOTIMG_REQUIRED_BYTES:-${baseline_boot_size:-${rom_boot_size:-134217728}}}"

# Preferred ROM-aligned fallback order:
# 1. Local/external official ROM package or extracted ROM directory
# 2. Local repository-side boot baseline when manually present outside git
# 3. External boot baseline URL pinned in BootImageBaseline.env
if [[ -n "$rom_source_used" ]]; then
  if [[ "$rom_source_used" == *"://"* ]]; then
    official_rom_dl="$ART/official-rom-baseline.img"
    if fetch_file "$rom_source_used" "$official_rom_dl"; then
      prepare_prebuilt_bootimg "$official_rom_dl" "baseline_url" "$rom_source_used"
    fi
  fi
  extract_rom_support_images "$rom_source_used"
  prepare_official_rom_bootimg
fi

# fallback: use a prebuilt boot.img directly when mkbootimg inputs are unavailable
if [[ -n "$prebuilt_url" ]]; then
  out_boot="$ART/boot.img"
  prebuilt_dl="$ART/prebuilt-download"
  tmp_boot="$ART/prebuilt-boot.img"
  rm -f "$out_boot" "$tmp_boot"
  if fetch_file "$prebuilt_url" "$prebuilt_dl"; then
    prepare_prebuilt_bootimg "$prebuilt_dl" "prebuilt_url" "$prebuilt_url"
  fi
  if [[ -f "$prebuilt_dl" ]]; then
    {
      echo "status=blocked"
      echo "reason=prebuilt-not-android-bootimg"
      echo "missing=valid_prebuilt_bootimg"
      echo "kernel_path=$kernel_path"
      echo "ramdisk_path=$ramdisk_path"
      echo "dtb_path=$dtb_path"
      echo "mkbootimg_cmd=$mkbootimg_cmd"
      echo "header_version=$header_version"
      echo "base=$base"
      echo "pagesize=$pagesize"
      echo "source=prebuilt_url"
      echo "prebuilt_url=$prebuilt_url"
    } > "$OUT"
    echo "bootimg build blocked: prebuilt payload is not a valid Android boot image"
    exit 0
  fi
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
    echo "baseline_bootimg_url=$rom_baseline_bootimg_url"
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
