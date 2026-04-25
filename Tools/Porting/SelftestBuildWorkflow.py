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
    expect_contains(text, 'echo "KERNEL_REPO=$TARGET_REPO" >> "$GITHUB_ENV"')
    expect_contains(text, 'echo "KERNEL_BRANCH=$TARGET_BRANCH" >> "$GITHUB_ENV"')
    expect_not_contains(text, 'echo "KERNEL_REPO=$SOURCE_REPO" >> "$GITHUB_ENV"')
    expect_not_contains(text, 'echo "KERNEL_BRANCH=$SOURCE_BRANCH" >> "$GITHUB_ENV"')
    print("build workflow uses 6+ target repository")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
