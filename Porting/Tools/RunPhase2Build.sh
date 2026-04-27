#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   RunPhase2Build.sh <device>

DEVICE="${1:-${DEVICE:-umi}}"

source "Porting/Tools/Common.sh"
initialize_porting_paths
python_cmd="$(resolve_python_cmd || true)"

if [[ -z "$python_cmd" ]]; then
  mkdir -p "$ARTIFACTS_DIR"
  echo "python interpreter not found" > "$ARTIFACTS_DIR/make-dtb-manifest.log"
  exit 1
fi

mkdir -p "$OUT_DIR" "$ARTIFACTS_DIR"
set +e
make -C "$KERNEL_DIR" O="$OUT_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 "${DEVICE}_defconfig" > "$ARTIFACTS_DIR/make-defconfig.log" 2>&1
rc1=$?

# Core build for packaging/readiness (fatal on failure)
make -C "$KERNEL_DIR" O="$OUT_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 -j"$(nproc)" Image.gz > "$ARTIFACTS_DIR/make-build.log" 2>&1
rc2=$?

# Build preferred DTBs from migrated manifest first (non-fatal for phase2 progression)
"$python_cmd" Porting/Tools/BuildDtbManifest.py > "$ARTIFACTS_DIR/make-dtb-manifest.log" 2>&1
rc_manifest=$?
rc3=0
: > "$ARTIFACTS_DIR/make-target-dtbs.log"
if [ -s "$ARTIFACTS_DIR/target_dtb_manifest.txt" ]; then
  while IFS= read -r dtb; do
    [ -n "$dtb" ] || continue

    # use canonical target form used by this target tree
    make -C "$KERNEL_DIR" O="$OUT_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 "qcom/$dtb" >> "$ARTIFACTS_DIR/make-target-dtbs.log" 2>&1
    r=$?
    if [ "$r" -ne 0 ]; then
      rc3=$r
    fi
  done < "$ARTIFACTS_DIR/target_dtb_manifest.txt"
else
  # Fallback to matrix dtbs build for diagnostics only
  make -C "$KERNEL_DIR" O="$OUT_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 -j"$(nproc)" dtbs > "$ARTIFACTS_DIR/make-target-dtbs.log" 2>&1
  rc3=$?
fi
set -e

{
  echo "defconfig_rc=$rc1"
  echo "build_rc=$rc2"
  echo "dtbs_rc=$rc3"
  echo "dtb_manifest_rc=$rc_manifest"
} > "$ARTIFACTS_DIR/build-exit.txt"

# fail only when defconfig or core build failed
if [ "$rc1" -ne 0 ] || [ "$rc2" -ne 0 ]; then
  exit 1
fi
