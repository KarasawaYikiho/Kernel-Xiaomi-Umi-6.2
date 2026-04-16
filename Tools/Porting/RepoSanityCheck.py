#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
import py_compile
import subprocess

ROOT = Path(__file__).resolve().parents[2]
TOOLS_PORTING = ROOT / "Tools" / "Porting"
PORTING_DOCS = ROOT / "Porting"
GITIGNORE = ROOT / ".gitignore"
REQUIRED_IGNORES = (
    "artifacts/",
    "source/",
    "target/",
    ".ruff_cache/",
    "__pycache__/",
)
TRACKED_GENERATED_PREFIXES = (
    "artifacts/",
    "source/",
    "target/",
)
TRACKED_GENERATED_SUFFIXES = (".pyc",)


def check_python_compile() -> list[str]:
    errs: list[str] = []
    py_files = sorted(TOOLS_PORTING.glob("*.py"))
    if not py_files:
        return ["no python files found under Tools/Porting"]
    for p in py_files:
        try:
            py_compile.compile(str(p), doraise=True)
        except Exception as e:  # pragma: no cover
            errs.append(f"py_compile failed: {p.relative_to(ROOT)} :: {e}")
    return errs


def check_workflow_script_refs() -> list[str]:
    errs: list[str] = []
    wf = ROOT / ".github" / "workflows" / "ROM-Aligned-Umi-Port.yml"
    if not wf.exists():
        return ["missing workflow: .github/workflows/ROM-Aligned-Umi-Port.yml"]
    text = wf.read_text(encoding="utf-8")

    sh_refs = re.findall(r"\./Tools/Porting/([\w\-]+\.sh)", text)
    py_refs = re.findall(r"python3?\s+Tools/Porting/([\w\-]+\.py)", text)

    for r in sorted(set(sh_refs)):
        if not (TOOLS_PORTING / r).exists():
            errs.append(f"missing script referenced by workflow: Tools/Porting/{r}")

    for r in sorted(set(py_refs)):
        if not (TOOLS_PORTING / r).exists():
            errs.append(
                f"missing python tool referenced by workflow: Tools/Porting/{r}"
            )

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
        proc = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception as exc:  # pragma: no cover
        return [f"unable to inspect tracked files via git: {exc}"]

    tracked = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    for path in tracked:
        normalized = path.replace("\\", "/")
        if normalized.startswith(TRACKED_GENERATED_PREFIXES):
            errs.append(f"tracked generated path: {normalized}")
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
    errors.extend(check_markdown_links())
    errors.extend(check_generated_dirs_ignored())
    errors.extend(check_tracked_generated_content())

    report = {
        "ok": len(errors) == 0,
        "error_count": len(errors),
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
