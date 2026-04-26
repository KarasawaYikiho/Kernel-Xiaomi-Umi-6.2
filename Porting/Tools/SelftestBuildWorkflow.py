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
    expect_contains(text, 'make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 umi_defconfig')
    expect_contains(text, 'make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 -j"$(nproc)" Image.gz modules dtbs')
    expect_contains(text, 'cp -v out/.config artifacts/ || true')
    expect_contains(text, 'cp -v out/arch/arm64/boot/Image.gz artifacts/ || true')
    expect_not_contains(text, 'working-directory: kernel')
    expect_not_contains(text, 'git clone --depth=1')
    expect_not_contains(text, '"$TARGET_REPO" kernel')
    expect_not_contains(text, '"$TARGET_REPO" target')
    expect_not_contains(text, 'build.sh')
    expect_not_contains(text, 'echo "KERNEL_REPO=$SOURCE_REPO" >> "$GITHUB_ENV"')
    expect_not_contains(text, 'echo "KERNEL_BRANCH=$SOURCE_BRANCH" >> "$GITHUB_ENV"')
    print("build workflow uses checked-out kernel source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
