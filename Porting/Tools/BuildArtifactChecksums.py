#!/usr/bin/env python3
from pathlib import Path
import hashlib

ART = Path("artifacts")
OUT = ART / "artifact-sha256.txt"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    files = sorted([p for p in ART.rglob("*") if p.is_file() and p.name != OUT.name])

    lines = [f"file_count={len(files)}"]
    for f in files:
        rel = f.relative_to(ART).as_posix()
        lines.append(f"{sha256_file(f)}  {rel}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
