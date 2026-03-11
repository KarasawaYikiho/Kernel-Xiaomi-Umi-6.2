#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "artifact-index.txt"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    files = sorted([p for p in ART.rglob("*") if p.is_file()])

    lines = [f"file_count={len(files)}"]
    for f in files:
        rel = f.relative_to(ART).as_posix()
        size = f.stat().st_size
        lines.append(f"{rel}\t{size}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
