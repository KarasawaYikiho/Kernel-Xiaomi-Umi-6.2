#!/usr/bin/env bash
set -euo pipefail

mkdir -p artifacts
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
  elif [ -d Tools/Porting/AnyKernel3Template ]; then
    template_source=repo-template
    template_dir=Tools/Porting/AnyKernel3Template
  else
    anykernel_reason=template-missing
  fi

  if [ -n "$template_dir" ] && [ -d "$template_dir" ]; then
    if command -v zip >/dev/null 2>&1; then
      anykernel_reason=zip-build-failed
      rm -rf "$work_dir"
      mkdir -p "$work_dir"
      cp -Rv "$template_dir"/. "$work_dir"/ || true
      cp -v "$imagegz_path" "$work_dir/Image.gz" || true

      # Optional: include first matched umi-related dtb as dtb
      if [ -s artifacts/umi_primary_dtb_paths.txt ]; then
        first_dtb="$(head -n1 artifacts/umi_primary_dtb_paths.txt)"
        if [ -f "$first_dtb" ]; then
          cp -v "$first_dtb" "$work_dir/dtb" || true
          anykernel_has_dtb=yes
          anykernel_dtb_source="$first_dtb"
        fi
      fi

      # Best-effort device hint
      sed -i 's/^  echo "device.name1=.*/  echo "device.name1=umi"/' "$work_dir/anykernel.sh" || true

      if (cd "$work_dir" && zip -r9 ../AnyKernel3-umi-candidate.zip .); then
        anykernel_ok=yes
        anykernel_reason=ok
      fi
    else
      anykernel_reason=zip-command-missing
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
