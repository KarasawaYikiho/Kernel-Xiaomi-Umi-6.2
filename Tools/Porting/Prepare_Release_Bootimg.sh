#!/usr/bin/env bash
set -euo pipefail

# Best-effort release boot.img preparation.
# Requires kernel image + ramdisk + mkbootimg parameters.
# Writes artifacts/bootimg-build.txt with explicit blockers when inputs are missing.

ART=artifacts
mkdir -p "$ART"
OUT="$ART/bootimg-build.txt"
DEFAULT_OFFICIAL_ROM_ZIP='D:\GIT\MIUI_UMI_OS1.0.5.0.TJBCNXM_d01651ed86_13.0.zip'

kernel_path=""
ramdisk_path="${BOOTIMG_RAMDISK_PATH:-}"
ramdisk_url="${BOOTIMG_RAMDISK_URL:-}"
prebuilt_url="${BOOTIMG_PREBUILT_URL:-}"
dtb_path="${BOOTIMG_DTB_PATH:-}"
mkbootimg_cmd=""
official_rom_zip="${OFFICIAL_ROM_ZIP:-$DEFAULT_OFFICIAL_ROM_ZIP}"
python_cmd=""

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
  local zip_path="$1"
  local tmp_dtbo="$ART/rom-dtbo.tmp"
  local tmp_vbmeta="$ART/rom-vbmeta.tmp"
  extract_named_from_zip "$zip_path" "firmware-update/dtbo.img" "$ART/dtbo.img" "$tmp_dtbo" || true
  extract_named_from_zip "$zip_path" "firmware-update/vbmeta.img" "$ART/vbmeta.img" "$tmp_vbmeta" || true
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

header_version="${BOOTIMG_HEADER_VERSION:-3}"
base="${BOOTIMG_BASE:-0x00000000}"
pagesize="${BOOTIMG_PAGESIZE:-4096}"
cmdline="${BOOTIMG_CMDLINE:-}"
required_bytes="${BOOTIMG_REQUIRED_BYTES:-134217728}"

# preferred ROM-aligned fallback: use local official ROM package when available
if [[ -f "$official_rom_zip" ]]; then
  extract_rom_support_images "$official_rom_zip"
  prepare_prebuilt_bootimg "$official_rom_zip" "official_rom_zip" "$official_rom_zip"
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
