#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "Build-Umi-Kernel.yml"


def expect_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing expected workflow line: {needle}")


def expect_not_contains(text: str, needle: str) -> None:
    if needle in text:
        raise AssertionError(f"unexpected workflow line: {needle}")


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    expect_contains(text, "branches:\n      - master")
    expect_contains(text, "if: github.ref == 'refs/heads/master'")
    expect_contains(text, 'echo "KERNEL_DIR=$GITHUB_WORKSPACE" >> "$GITHUB_ENV"')
    expect_contains(text, 'echo "OUT_DIR=$GITHUB_WORKSPACE/out" >> "$GITHUB_ENV"')
    expect_contains(text, "DEVICE: ${{ github.event.inputs.device || 'umi' }}")
    expect_contains(text, 'python3 Porting/Tools/ValidatePortDevice.py "$DEVICE"')
    expect_contains(text, "find scripts arch tools -type f -exec sh -c '")
    expect_contains(text, "head -c 2 \"$1\"")
    expect_contains(text, "mkdir -p artifacts")
    expect_contains(text, "> artifacts/make-defconfig.log 2>&1")
    expect_contains(text, "> artifacts/make-build.log 2>&1")
    expect_contains(text, "defconfig_rc=$rc1")
    expect_contains(text, "build_rc=$rc2")
    expect_contains(text, 'make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 umi_defconfig')
    expect_contains(text, 'make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 -j"$(nproc)" Image.gz dtbs')
    expect_contains(text, "if: always()")
    expect_contains(text, 'cp -v out/.config artifacts/ || true')
    expect_contains(text, 'cp -v out/arch/arm64/boot/Image.gz artifacts/ || true')
    expect_not_contains(text, 'working-directory: kernel')
    expect_not_contains(text, 'git clone --depth=1')
    expect_not_contains(text, '"$TARGET_REPO" kernel')
    expect_not_contains(text, '"$TARGET_REPO" target')
    expect_not_contains(text, 'build.sh')
    expect_not_contains(text, 'echo "KERNEL_REPO=$SOURCE_REPO" >> "$GITHUB_ENV"')
    expect_not_contains(text, 'echo "KERNEL_BRANCH=$SOURCE_BRANCH" >> "$GITHUB_ENV"')

    phase2 = (ROOT / "Porting" / "Tools" / "RunPhase2Build.sh").read_text(
        encoding="utf-8"
    )
    expect_contains(phase2, 'ARCH=arm64')
    expect_contains(phase2, '"$KERNEL_DIR/scripts" "$KERNEL_DIR/arch" "$KERNEL_DIR/tools"')
    expect_contains(phase2, 'head -c 2 "$1"')
    expect_contains(phase2, 'make -C "$KERNEL_DIR" O="$OUT_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 "${DEVICE}_defconfig"')
    expect_contains(phase2, 'make -C "$KERNEL_DIR" O="$OUT_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 -j"$(nproc)" Image.gz')
    expect_not_contains(phase2, 'Image.gz modules')
    expect_contains(phase2, 'make -C "$KERNEL_DIR" O="$OUT_DIR" ARCH=arm64 LLVM=1 LLVM_IAS=1 "qcom/$dtb"')
    expect_contains(phase2, "::error title=Phase2 kernel build failed::defconfig_rc=$rc1 build_rc=$rc2")

    anykernel = (ROOT / "Porting" / "Tools" / "BuildAnyKernelCandidate.sh").read_text(
        encoding="utf-8"
    )
    expect_contains(anykernel, "python3 - <<'PY'")
    expect_not_contains(anykernel, "zip-command-missing")

    postprocess = (ROOT / "Porting" / "Tools" / "RunPostprocessSuite.sh").read_text(
        encoding="utf-8"
    )
    prepare_idx = postprocess.find('"PrepareReleaseBootImg.sh"')
    validate_idx = postprocess.find('"ValidateBootImage.py"')
    if prepare_idx < 0 or validate_idx < 0 or prepare_idx > validate_idx:
        raise AssertionError("postprocess must prepare boot.img before validating it")
    print("build workflow uses checked-out kernel source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
