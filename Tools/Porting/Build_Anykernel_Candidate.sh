#!/usr/bin/env bash
set -euo pipefail

mkdir -p artifacts
anykernel_ok=no
anykernel_has_imagegz=no
anykernel_has_dtb=no
anykernel_dtb_source=

if [ -f out/arch/arm64/boot/Image.gz ]; then
  anykernel_has_imagegz=yes
  rm -rf anykernel3
  git clone --depth=1 https://github.com/osm0sis/AnyKernel3.git anykernel3 || true
  if [ -d anykernel3 ]; then
    cp -v out/arch/arm64/boot/Image.gz anykernel3/Image.gz || true

    # Optional: include first matched umi-related dtb as dtb
    if [ -s artifacts/umi_primary_dtb_paths.txt ]; then
      first_dtb="$(head -n1 artifacts/umi_primary_dtb_paths.txt)"
      if [ -f "$first_dtb" ]; then
        cp -v "$first_dtb" anykernel3/dtb || true
        anykernel_has_dtb=yes
        anykernel_dtb_source="$first_dtb"
      fi
    fi

    # Best-effort device hint
    sed -i 's/^device.name1=.*/device.name1=umi/' anykernel3/anykernel.sh || true

    if (cd anykernel3 && zip -r9 ../artifacts/AnyKernel3-umi-candidate.zip . -x ".git/*"); then
      anykernel_ok=yes
    fi
  fi
fi

{
  echo "anykernel_ok=$anykernel_ok"
  echo "has_imagegz=$anykernel_has_imagegz"
  echo "has_dtb=$anykernel_has_dtb"
  echo "dtb_source=$anykernel_dtb_source"
} > artifacts/anykernel-info.txt
