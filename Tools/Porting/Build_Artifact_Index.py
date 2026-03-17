#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "artifact-index.txt"

PRIORITY_ORDER = [
    "runtime-validation-summary.md",
    "runtime-validation-input.md",
    "runtime-validation-result.txt",
    "phase2-report.txt",
    "status-badge-line.txt",
    "action-validation-checklist.md",
    "artifact-summary.md",
    "next-focus.txt",
    "build-error-summary.txt",
    "anykernel-info.txt",
]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    files = sorted([p for p in ART.rglob("*") if p.is_file()])
    present = {p.relative_to(ART).as_posix() for p in files}
    priority_files = [p for p in PRIORITY_ORDER if p in present]

    lines = [f"file_count={len(files)}", "priority_files=" + ",".join(priority_files)]
    for f in files:
        rel = f.relative_to(ART).as_posix()
        size = f.stat().st_size
        marker = "\tpriority" if rel in priority_files else ""
        lines.append(f"{rel}\t{size}{marker}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
