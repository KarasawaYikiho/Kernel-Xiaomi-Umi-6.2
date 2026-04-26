#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

import RepoSanityCheck


class FakeCompletedProcess:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def assert_tracked_content_scan_uses_git_grep() -> None:
    calls: list[list[str]] = []
    original_run = RepoSanityCheck.subprocess.run

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        if cmd[:2] == ["git", "grep"]:
            return FakeCompletedProcess(
                0,
                "Docs/Sample.md:7:ROM path: D:\\GIT\\MIUI_UMI\\boot.img\n",
            )
        raise AssertionError(f"unexpected subprocess call: {cmd}")

    RepoSanityCheck.subprocess.run = fake_run
    try:
        errors = RepoSanityCheck.check_no_local_paths_in_tracked_content()
    finally:
        RepoSanityCheck.subprocess.run = original_run

    if not any(call[:2] == ["git", "grep"] for call in calls):
        raise AssertionError("expected tracked content scan to use git grep")
    if errors != ["local machine path in tracked content: Docs/Sample.md:7"]:
        raise AssertionError(f"unexpected git grep local path errors: {errors}")


def assert_tracked_content_scan_accepts_no_matches() -> None:
    original_run = RepoSanityCheck.subprocess.run

    def fake_run(cmd, **kwargs):
        if cmd[:2] == ["git", "grep"]:
            return FakeCompletedProcess(1)
        raise AssertionError(f"unexpected subprocess call: {cmd}")

    RepoSanityCheck.subprocess.run = fake_run
    try:
        errors = RepoSanityCheck.check_no_local_paths_in_tracked_content()
    finally:
        RepoSanityCheck.subprocess.run = original_run

    if errors:
        raise AssertionError(f"expected no local path errors for git grep miss: {errors}")


def main() -> int:
    assert_tracked_content_scan_uses_git_grep()
    assert_tracked_content_scan_accepts_no_matches()

    with tempfile.TemporaryDirectory(prefix="repo-sanity-local-path-") as tmpdir:
        sample = Path(tmpdir) / "Sample.md"
        sample.write_text("ROM path: D:\\GIT\\MIUI_UMI\\boot.img\n", encoding="utf-8")
        errors = RepoSanityCheck.check_no_local_paths_in_files([sample])

    if not errors:
        raise AssertionError("expected local path leak to be reported")
    if "Sample.md" not in errors[0]:
        raise AssertionError(f"expected filename in local path error: {errors[0]}")

    print("repo-sanity-local-path-selftest=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
