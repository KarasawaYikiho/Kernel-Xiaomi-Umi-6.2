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


def sample_local_path() -> str:
    return "D:" + "\\" + "G" + "IT" + "\\" + "MIUI" + "_" + "UMI" + "\\" + "boot.img"


def assert_tracked_content_scan_uses_git_grep() -> None:
    calls: list[list[str]] = []
    original_run = RepoSanityCheck.subprocess.run

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))
        if cmd[:2] == ["git", "grep"]:
            return FakeCompletedProcess(
                0,
                f"Docs/Sample.md:7:ROM path: {sample_local_path()}\n",
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


def assert_required_ignores_cover_local_anykernel_and_rom_archives() -> None:
    required = set(RepoSanityCheck.REQUIRED_IGNORES)
    expected = {"/anykernel3/", "Porting/OfficialRomBaseline/*.zip"}
    missing = sorted(expected - required)
    if missing:
        raise AssertionError(f"missing local input ignore requirements: {missing}")


def assert_github_standard_templates_do_not_fail_titlecase_check() -> None:
    original_list_tracked_files = RepoSanityCheck.list_tracked_files

    def fake_list_tracked_files() -> list[str]:
        return [
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/config.yml",
            ".github/PULL_REQUEST_TEMPLATE.md",
            "Porting/Tools/RepoSanityCheck.py",
        ]

    RepoSanityCheck.list_tracked_files = fake_list_tracked_files
    try:
        errors = RepoSanityCheck.check_tracked_names()
    finally:
        RepoSanityCheck.list_tracked_files = original_list_tracked_files

    if errors:
        raise AssertionError(f"expected GitHub standard templates to be exempt: {errors}")


def assert_localized_root_docs_are_checked_for_titlecase() -> None:
    required = {"ReadmeZhCn.md", "ContributingZhCn.md"}
    missing = required - set(RepoSanityCheck.PROJECT_NAME_CHECK_ROOT_FILES)
    if missing:
        raise AssertionError(f"localized root docs missing from titlecase check: {sorted(missing)}")


def assert_repo_url_is_not_local_path_leak() -> None:
    with tempfile.TemporaryDirectory(prefix="repo-sanity-repo-url-") as tmpdir:
        sample = Path(tmpdir) / "Sample.md"
        sample.write_text(
            "Docs: https://github.com/KarasawaYikiho/Kernel-Xiaomi-Umi-6.11\n",
            encoding="utf-8",
        )
        errors = RepoSanityCheck.check_no_local_paths_in_files([sample])

    if errors:
        raise AssertionError(f"expected repository URL not to be a local path: {errors}")


def main() -> int:
    assert_tracked_content_scan_uses_git_grep()
    assert_tracked_content_scan_accepts_no_matches()
    assert_required_ignores_cover_local_anykernel_and_rom_archives()
    assert_github_standard_templates_do_not_fail_titlecase_check()
    assert_localized_root_docs_are_checked_for_titlecase()
    assert_repo_url_is_not_local_path_leak()

    with tempfile.TemporaryDirectory(prefix="repo-sanity-local-path-") as tmpdir:
        sample = Path(tmpdir) / "Sample.md"
        sample.write_text(f"ROM path: {sample_local_path()}\n", encoding="utf-8")
        errors = RepoSanityCheck.check_no_local_paths_in_files([sample])

    if not errors:
        raise AssertionError("expected local path leak to be reported")
    if "Sample.md" not in errors[0]:
        raise AssertionError(f"expected filename in local path error: {errors[0]}")

    print("repo-sanity-local-path-selftest=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
