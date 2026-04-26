#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path

import RepoSanityCheck


def main() -> int:
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
