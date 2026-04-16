#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ART = Path("artifacts")
ROOT = Path("out/arch/arm64/boot/dts")
OUT = ART / "all_dtb_paths.txt"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    if not ROOT.exists():
        OUT.write_text("", encoding="utf-8")
        print(f"wrote {OUT} (missing dts root)")
        return 0

    items: list[str] = []
    for suffix in ("*.dtb", "*.dtbo"):
        for path in ROOT.rglob(suffix):
            if path.is_file():
                items.append(path.as_posix())

    items = sorted(dict.fromkeys(items))
    OUT.write_text("\n".join(items) + ("\n" if items else ""), encoding="utf-8")
    print(f"wrote {OUT} ({len(items)} paths)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
