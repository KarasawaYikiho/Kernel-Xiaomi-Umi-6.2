#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
import py_compile
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
TOOLS_PORTING = ROOT / "Porting" / "Tools"
PORTING_DOCS = ROOT / "Porting"
GITIGNORE = ROOT / ".gitignore"
TOKEN_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
PROJECT_NAME_CHECK_PREFIXES = (
    "Porting/",
)
PROJECT_NAME_CHECK_ROOT_FILES = {
    "AGENTS.md",
    "ContributingZhCn.md",
    "PortingPlan.md",
    "ReadmeZhCn.md",
}
REQUIRED_IGNORES = (
    "/artifacts/",
    "/out/",
    "/source/",
    "/target/",
    "/source.extract/",
    "/target.extract/",
    "source.zip",
    "/anykernel3/",
    "Porting/OfficialRomBaseline/*.zip",
    ".ruff_cache/",
    "__pycache__/",
)
TRACKED_GENERATED_PREFIXES = (
    "artifacts/",
    "source/",
    "target/",
    "source.extract/",
    "target.extract/",
)
TRACKED_GENERATED_FILES = ("source.zip",)
TRACKED_GENERATED_SUFFIXES = (".pyc",)
TEXT_SCAN_SKIP_SUFFIXES = (
    ".bin",
    ".bmp",
    ".dtb",
    ".elf",
    ".gz",
    ".img",
    ".jpg",
    ".jpeg",
    ".o",
    ".png",
    ".so",
    ".xz",
    ".zip",
)
LOCAL_ROM_ROOT = "G" + "IT"
LOCAL_USER = "D" + "2O"
LOCAL_WORKSPACE_NAME = "Kernel-" + "Xiaomi-" + "Umi-6.12"
LOCAL_PATH_PATTERNS = (
    re.compile(rf"\b[A-Za-z]:[\\/]{LOCAL_ROM_ROOT}[\\/][^\s`'\")]+", re.IGNORECASE),
    re.compile(rf"\b[A-Za-z]:[\\/]Users[\\/]{LOCAL_USER}[\\/][^\s`'\")]+", re.IGNORECASE),
    re.compile(rf"/mnt/[A-Za-z]/Users/{LOCAL_USER}/[^\s`'\")]+", re.IGNORECASE),
    re.compile(rf"(?:^|[\\/])Users[\\/]{LOCAL_USER}[\\/][^\s`'\")]+", re.IGNORECASE),
)
LOCAL_PATH_GREP_PATTERN = (
    rf"([A-Za-z]:[\\/]{LOCAL_ROM_ROOT}[\\/][^[:space:]`'\")]+"
    rf"|[A-Za-z]:[\\/]Users[\\/]{LOCAL_USER}[\\/][^[:space:]`'\")]+"
    rf"|/mnt/[A-Za-z]/Users/{LOCAL_USER}/[^[:space:]`'\")]+"
    rf"|(^|[\\/])Users[\\/]{LOCAL_USER}[\\/][^[:space:]`'\")]+)"
)


def list_tracked_files() -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"unable to inspect tracked files via git: {exc}") from exc
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def is_valid_name(name: str) -> bool:
    if not name:
        return False
    tokens = [tok for tok in re.split(r"[\s_-]+", name) if tok]
    return bool(tokens) and all(TOKEN_RE.fullmatch(tok) for tok in tokens)


def check_tracked_names() -> list[str]:
    errs: list[str] = []
    try:
        tracked = list_tracked_files()
    except RuntimeError as exc:  # pragma: no cover
        return [str(exc)]

    for path in tracked:
        normalized = path.replace("\\", "/")
        if not (
            normalized in PROJECT_NAME_CHECK_ROOT_FILES
            or normalized.startswith(PROJECT_NAME_CHECK_PREFIXES)
        ):
            continue

        rel = Path(path)
        if any(part.startswith(".") for part in rel.parts):
            continue

        for part in rel.parts[:-1]:
            if not is_valid_name(part):
                errs.append(f"tracked path has non-conforming folder name: {path}")
                break
        else:
            if not is_valid_name(rel.stem):
                errs.append(f"tracked path has non-conforming file name: {path}")

    return errs


def check_no_local_paths_in_files(paths: list[Path]) -> list[str]:
    errs: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in LOCAL_PATH_PATTERNS:
                if pattern.search(line):
                    try:
                        shown = path.relative_to(ROOT)
                    except ValueError:
                        shown = path
                    errs.append(f"local machine path in tracked content: {shown}:{lineno}")
                    break
    return errs


def check_no_local_paths_in_tracked_content() -> list[str]:
    proc = subprocess.run(
        ["git", "grep", "-I", "-n", "-E", LOCAL_PATH_GREP_PATTERN, "--", "."],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 1:
        return []
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "unknown git grep error"
        return [f"unable to inspect tracked files via git grep: {detail}"]

    errs: list[str] = []
    for line in proc.stdout.splitlines():
        path, sep, rest = line.partition(":")
        lineno, line_sep, _content = rest.partition(":")
        if sep and line_sep and lineno.isdigit():
            errs.append(f"local machine path in tracked content: {path}:{lineno}")
        else:
            errs.append(f"local machine path in tracked content: {line}")
    return errs


def check_python_compile() -> list[str]:
    errs: list[str] = []
    py_files = sorted(TOOLS_PORTING.glob("*.py"))
    if not py_files:
        return ["no python files found under Porting/Tools"]
    with tempfile.TemporaryDirectory(prefix="repo-sanity-pyc-") as tmpdir:
        tmp_root = Path(tmpdir)
        for p in py_files:
            try:
                cfile = tmp_root / f"{p.stem}.pyc"
                py_compile.compile(str(p), cfile=str(cfile), doraise=True)
            except Exception as e:  # pragma: no cover
                errs.append(f"py_compile failed: {p.relative_to(ROOT)} :: {e}")
    return errs


def check_workflow_script_refs() -> list[str]:
    errs: list[str] = []
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    if not workflows:
        return ["missing workflows under .github/workflows"]

    for wf in workflows:
        text = wf.read_text(encoding="utf-8")
        sh_refs = re.findall(r"\./Porting/Tools/([\w\-]+\.sh)", text)
        py_refs = re.findall(r"python3?\s+Porting/Tools/([\w\-]+\.py)", text)

        for r in sorted(set(sh_refs)):
            if not (TOOLS_PORTING / r).exists():
                errs.append(
                    f"missing script referenced by workflow {wf.name}: Porting/Tools/{r}"
                )

        for r in sorted(set(py_refs)):
            if not (TOOLS_PORTING / r).exists():
                errs.append(
                    f"missing python tool referenced by workflow {wf.name}: Porting/Tools/{r}"
                )

    return errs


def check_workflow_no_raw_urls() -> list[str]:
    errs: list[str] = []
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        for match in re.finditer(r"https?://\S+", text):
            errs.append(f"raw url in workflow {wf.name}: {match.group(0)}")
    return errs


def check_markdown_links() -> list[str]:
    errs: list[str] = []
    md_files = list(ROOT.glob("*.md"))
    md_files += list(PORTING_DOCS.glob("*.md"))
    md_files += list(TOOLS_PORTING.glob("*.md"))

    for md in md_files:
        txt = md.read_text(encoding="utf-8")
        for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", txt):
            link = m.group(1).strip().strip("<>")
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if link.startswith("./"):
                link = link[2:]
            target = (md.parent / link).resolve()
            if not target.exists():
                errs.append(f"broken link: {md.relative_to(ROOT)} -> {link}")
    return errs


def check_generated_dirs_ignored() -> list[str]:
    errs: list[str] = []
    if not GITIGNORE.exists():
        return ["missing .gitignore"]

    entries = {
        line.strip()
        for line in GITIGNORE.read_text(encoding="utf-8", errors="ignore").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    for entry in REQUIRED_IGNORES:
        if entry not in entries:
            errs.append(f"missing ignore rule: {entry}")

    return errs


def check_tracked_generated_content() -> list[str]:
    errs: list[str] = []
    try:
        tracked = list_tracked_files()
    except RuntimeError as exc:  # pragma: no cover
        return [str(exc)]

    for path in tracked:
        normalized = path.replace("\\", "/")
        if normalized.startswith(TRACKED_GENERATED_PREFIXES):
            errs.append(f"tracked generated path: {normalized}")
            continue
        if normalized in TRACKED_GENERATED_FILES:
            errs.append(f"tracked generated file: {normalized}")
            continue
        if "/__pycache__/" in f"/{normalized}" or normalized.endswith("/__pycache__"):
            errs.append(f"tracked cache path: {normalized}")
            continue
        if normalized.endswith(TRACKED_GENERATED_SUFFIXES):
            errs.append(f"tracked compiled artifact: {normalized}")

    return errs


def main() -> int:
    errors = []
    errors.extend(check_python_compile())
    errors.extend(check_workflow_script_refs())
    errors.extend(check_workflow_no_raw_urls())
    errors.extend(check_markdown_links())
    errors.extend(check_generated_dirs_ignored())
    errors.extend(check_tracked_generated_content())
    errors.extend(check_tracked_names())
    errors.extend(check_no_local_paths_in_tracked_content())

    report = {
        "ok": len(errors) == 0,
        "error_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
