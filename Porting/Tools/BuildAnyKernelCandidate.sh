#!/usr/bin/env bash
set -euo pipefail

mkdir -p artifacts
DEVICE="${DEVICE:-umi}"
anykernel_ok=no
anykernel_has_imagegz=no
anykernel_has_dtb=no
anykernel_dtb_source=
anykernel_reason=imagegz-missing
imagegz_path=
template_source=
template_dir=
work_dir=artifacts/anykernel3-work

if [ -f out/arch/arm64/boot/Image.gz ]; then
  imagegz_path=out/arch/arm64/boot/Image.gz
elif [ -f artifacts/Image.gz ]; then
  imagegz_path=artifacts/Image.gz
fi

if [ -n "$imagegz_path" ]; then
  anykernel_has_imagegz=yes
  if [ -d anykernel3 ]; then
    template_source=existing-dir
    template_dir=anykernel3
  elif [ -d Porting/Tools/AnyKernel3Template ]; then
    template_source=repo-template
    template_dir=Porting/Tools/AnyKernel3Template
  else
    anykernel_reason=template-missing
  fi

  if [ -n "$template_dir" ] && [ -d "$template_dir" ]; then
    anykernel_reason=zip-build-failed
    rm -rf "$work_dir"
    mkdir -p "$work_dir"
    cp -Rv "$template_dir"/. "$work_dir"/ || true
    cp -v "$imagegz_path" "$work_dir/Image.gz" || true

    if [ -f "$work_dir/AnyKernel.sh" ]; then
      mv -f "$work_dir/AnyKernel.sh" "$work_dir/anykernel.sh"
    fi

    # Optional: include device-specific dtb first, fallback to first available
    if [ -s artifacts/primary_dtb_paths.txt ]; then
      device_dtb="$(grep -F "sm8250-xiaomi-${DEVICE:-umi}.dtb" artifacts/primary_dtb_paths.txt 2>/dev/null | head -n1 || true)"
      if [ -n "$device_dtb" ] && [ -f "$device_dtb" ]; then
        first_dtb="$device_dtb"
      else
        first_dtb="$(head -n1 artifacts/primary_dtb_paths.txt)"
      fi
      if [ -f "$first_dtb" ]; then
        cp -v "$first_dtb" "$work_dir/dtb" || true
        anykernel_has_dtb=yes
        anykernel_dtb_source="$first_dtb"
      fi
    fi

    # Best-effort device hint
    sed -i "s/^  echo \"device.name1=.*/  echo \"device.name1=$DEVICE\"/" "$work_dir/anykernel.sh" || true

    if command -v zip >/dev/null 2>&1; then
      if (cd "$work_dir" && zip -r9 ../AnyKernel3-candidate.zip .); then
        anykernel_ok=yes
        anykernel_reason=ok
      fi
    else
      WORK_DIR="$work_dir" python3 - <<'PY'
from __future__ import annotations

import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

work_dir = Path(os.environ["WORK_DIR"])
zip_path = work_dir.parent / "AnyKernel3-candidate.zip"
with ZipFile(zip_path, "w", ZIP_DEFLATED) as zf:
    for path in sorted(p for p in work_dir.rglob("*") if p.is_file()):
        zf.write(path, path.relative_to(work_dir).as_posix())
PY
      if [ -f artifacts/AnyKernel3-candidate.zip ]; then
        anykernel_ok=yes
        anykernel_reason=ok
      fi
    fi
  fi
fi

{
  echo "anykernel_ok=$anykernel_ok"
  echo "reason=$anykernel_reason"
  echo "has_imagegz=$anykernel_has_imagegz"
  echo "imagegz_path=$imagegz_path"
  echo "has_dtb=$anykernel_has_dtb"
  echo "dtb_source=$anykernel_dtb_source"
  echo "template_source=$template_source"
} > artifacts/anykernel-info.txt
