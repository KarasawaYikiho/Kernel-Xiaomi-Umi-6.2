#!/usr/bin/env python3
from pathlib import Path
import re

COPIED = Path("target/Porting/phase2/copied_dts.txt")
OUT = Path("artifacts/target_dtb_manifest.txt")
DEBUG_OUT = Path("artifacts/target_dtb_manifest_debug.txt")
TARGET_DTS_ROOTS = [
    Path("target/arch/arm64/boot/dts/qcom"),
    Path("target/arch/arm64/boot/dts/vendor/qcom"),
]

ALLOW = re.compile(r"(sm8250-xiaomi|umi-sm8250|xiaomi-sm8250-common|umi|sm8250)", re.I)
DENY = re.compile(r"(rumi|lumia|sony|hdk|mtp|edo|pdx)", re.I)
TOKEN_SPLIT = re.compile(r"[-_./]+")
PREFER = [
    re.compile(r"^(sm8250-xiaomi-umi.*)\.dtb$", re.I),
    re.compile(r"^(umi-sm8250.*)\.dtb$", re.I),
    re.compile(r"^(xiaomi-sm8250-common.*)\.dtb$", re.I),
]
CANONICAL_ALIASES = {
    "umi": [
        "sm8250-xiaomi-umi.dtb",
        "umi-sm8250.dtb",
        "xiaomi-sm8250-common.dtb",
    ],
}


def to_dtb_name(path_str: str) -> str | None:
    p = Path(path_str.strip())
    name = p.name
    if not name.endswith(".dts"):
        return None
    stem = name[:-4]
    if not ALLOW.search(stem):
        return None
    if DENY.search(stem):
        return None
    return stem + ".dtb"


def alias_names(path_str: str) -> list[str]:
    raw = path_str.strip()
    stem = Path(raw).stem.lower()
    tokens = {x for x in TOKEN_SPLIT.split(raw.lower()) if x}
    names: list[str] = []

    if "umi" in tokens or stem == "umi":
        names.extend(CANONICAL_ALIASES["umi"])
    if {"xiaomi", "sm8250", "umi"}.issubset(tokens):
        names.extend(CANONICAL_ALIASES["umi"])
    if stem == "xiaomi-sm8250-common":
        names.extend(CANONICAL_ALIASES["umi"])

    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for name in names:
        if name not in seen and not DENY.search(name):
            seen.add(name)
            out.append(name)
    return out


def rank_name(name: str) -> int:
    for i, p in enumerate(PREFER):
        if p.search(name):
            return i
    return len(PREFER)


def collect_from_copied() -> tuple[list[str], list[str]]:
    if not COPIED.exists():
        return [], []
    names: list[str] = []
    debug: list[str] = []
    for line in COPIED.read_text(encoding="utf-8", errors="ignore").splitlines():
        raw = line.strip()
        if not raw:
            continue
        n = to_dtb_name(line)
        if n:
            names.append(n)
            debug.append(f"copied_dts\tprimary\t{raw}\t{n}")
        aliases = alias_names(line)
        names.extend(aliases)
        for alias in aliases:
            debug.append(f"copied_dts\talias\t{raw}\t{alias}")
    return names, debug


def collect_from_target_tree() -> tuple[list[str], list[str]]:
    names: list[str] = []
    debug: list[str] = []
    for root in TARGET_DTS_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*.dts"):
            raw = str(p)
            n = to_dtb_name(raw)
            if n:
                names.append(n)
                debug.append(f"target_tree\tprimary\t{raw}\t{n}")
            aliases = alias_names(raw)
            names.extend(aliases)
            for alias in aliases:
                debug.append(f"target_tree\talias\t{raw}\t{alias}")
    return names, debug


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    names, debug = collect_from_copied()
    source = "copied_dts"
    if not names:
        names, debug = collect_from_target_tree()
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
    debug_lines = [
        f"source={source}",
        f"candidate_total={len(names)}",
        f"unique_total={len(uniq)}",
        "format=origin<TAB>kind<TAB>input<TAB>candidate",
    ]
    debug_lines.extend(debug)
    DEBUG_OUT.write_text("\n".join(debug_lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(uniq)} names, source={source})")
    print(f"wrote {DEBUG_OUT}")


if __name__ == "__main__":
    main()
