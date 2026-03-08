#!/usr/bin/env python3
from pathlib import Path
import re

COPIED = Path("target/porting/phase2/copied_dts.txt")
OUT = Path("artifacts/target_dtb_manifest.txt")

ALLOW = re.compile(r"(umi|sm8250|xiaomi|lmi|cmi|apollo|alioth|thyme)", re.I)
DENY = re.compile(r"(rumi|lumia|sony|hdk|mtp)", re.I)


def to_dtb_name(path_str: str) -> str | None:
    p = Path(path_str.strip())
    name = p.name
    if not name.endswith('.dts'):
        return None
    stem = name[:-4]
    if not ALLOW.search(stem):
        return None
    if DENY.search(stem):
        return None
    return stem + '.dtb'


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not COPIED.exists():
        OUT.write_text("", encoding="utf-8")
        print("manifest empty: copied_dts.txt missing")
        return

    names = []
    for line in COPIED.read_text(encoding="utf-8", errors="ignore").splitlines():
        n = to_dtb_name(line)
        if n:
            names.append(n)

    # dedupe while preserving order
    seen = set()
    uniq = []
    for n in names:
        if n not in seen:
            seen.add(n)
            uniq.append(n)

    OUT.write_text("\n".join(uniq) + ("\n" if uniq else ""), encoding="utf-8")
    print(f"wrote {OUT} ({len(uniq)} names)")


if __name__ == '__main__':
    main()
