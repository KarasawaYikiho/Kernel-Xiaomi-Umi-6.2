#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   Run_Phase2_Build.sh <device>

DEVICE="${1:-umi}"

mkdir -p out artifacts
set +e
make -C target O=$PWD/out LLVM=1 LLVM_IAS=1 "${DEVICE}_defconfig" > artifacts/make-defconfig.log 2>&1
rc1=$?

# Core build for packaging/readiness (fatal on failure)
make -C target O=$PWD/out LLVM=1 LLVM_IAS=1 -j"$(nproc)" Image.gz modules > artifacts/make-build.log 2>&1
rc2=$?

# Build preferred DTBs from migrated manifest first (non-fatal for phase2 progression)
python3 Tools/Porting/Build_Dtb_Manifest.py > artifacts/make-dtb-manifest.log 2>&1
rc_manifest=$?
rc3=0
: > artifacts/make-target-dtbs.log
if [ -s artifacts/target_dtb_manifest.txt ]; then
  while IFS= read -r dtb; do
    [ -n "$dtb" ] || continue

    # use canonical target form used by this target tree
    make -C target O=$PWD/out LLVM=1 LLVM_IAS=1 "qcom/$dtb" >> artifacts/make-target-dtbs.log 2>&1
    r=$?
    if [ "$r" -ne 0 ]; then
      rc3=$r
    fi
  done < artifacts/target_dtb_manifest.txt
else
  # Fallback to matrix dtbs build for diagnostics only
  make -C target O=$PWD/out LLVM=1 LLVM_IAS=1 -j"$(nproc)" dtbs > artifacts/make-target-dtbs.log 2>&1
  rc3=$?
fi
set -e

{
  echo "defconfig_rc=$rc1"
  echo "build_rc=$rc2"
  echo "dtbs_rc=$rc3"
  echo "dtb_manifest_rc=$rc_manifest"
} > artifacts/build-exit.txt

# fail only when defconfig or core build failed
if [ "$rc1" -ne 0 ] || [ "$rc2" -ne 0 ]; then
  exit 1
fi
