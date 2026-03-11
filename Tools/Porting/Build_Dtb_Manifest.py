#!/usr/bin/env python3
from pathlib import Path
import re

COPIED = Path("target/Porting/phase2/copied_dts.txt")
OUT = Path("artifacts/target_dtb_manifest.txt")
TARGET_DTS_ROOTS = [
    Path("target/arch/arm64/boot/dts/qcom"),
    Path("target/arch/arm64/boot/dts/vendor/qcom"),
]

ALLOW = re.compile(r"(sm8250-xiaomi|umi-sm8250|xiaomi-sm8250-common|umi|sm8250)", re.I)
DENY = re.compile(r"(rumi|lumia|sony|hdk|mtp|edo|pdx)", re.I)
PREFER = [
    re.compile(r"^(sm8250-xiaomi-umi.*)\.dtb$", re.I),
    re.compile(r"^(umi-sm8250.*)\.dtb$", re.I),
    re.compile(r"^(xiaomi-sm8250-common.*)\.dtb$", re.I),
]


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


def rank_name(name: str) -> int:
    for i, p in enumerate(PREFER):
        if p.search(name):
            return i
    return len(PREFER)


def collect_from_copied() -> list[str]:
    if not COPIED.exists():
        return []
    names: list[str] = []
    for line in COPIED.read_text(encoding="utf-8", errors="ignore").splitlines():
        n = to_dtb_name(line)
        if n:
            names.append(n)
    return names


def collect_from_target_tree() -> list[str]:
    names: list[str] = []
    for root in TARGET_DTS_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*.dts"):
            n = to_dtb_name(str(p))
            if n:
                names.append(n)
    return names


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    names = collect_from_copied()
    source = "copied_dts"
    if not names:
        names = collect_from_target_tree()
        source = "target_dts_scan"

    # dedupe while preserving order
    seen = set()
    uniq = []
    for n in names:
        if n not in seen:
            seen.add(n)
            uniq.append(n)

    # prefer umi-precise dtb names first, keep stable order inside each rank
    uniq.sort(key=lambda x: (rank_name(x), x))

    OUT.write_text("\n".join(uniq) + ("\n" if uniq else ""), encoding="utf-8")
    print(f"wrote {OUT} ({len(uniq)} names, source={source})")


if __name__ == '__main__':
    main()
