#!/usr/bin/env python3
from __future__ import annotations

import os
import re
from pathlib import Path

from KvUtils import parse_kv
from PortConfig import get_nested, get_supported_devices, load_port_config

OUT = Path("artifacts/target_dtb_manifest.txt")
DEBUG_OUT = Path("artifacts/target_dtb_manifest_debug.txt")
LOG_SOURCES = [
    ("target_copied", Path("target/Porting/phase2/copied_dts.txt")),
    ("target_seed", Path("target/Porting/phase2/seed_dts.txt")),
    ("target_included", Path("target/Porting/phase2/included_dts.txt")),
    ("artifact_copied", Path("artifacts/copied_dts.txt")),
    ("artifact_seed", Path("artifacts/seed_dts.txt")),
    ("artifact_included", Path("artifacts/included_dts.txt")),
]
TARGET_DTS_ROOTS = [
    Path("target/arch/arm64/boot/dts/qcom"),
    Path("target/arch/arm64/boot/dts/vendor/qcom"),
    Path("target/arch/arm64/boot/dts/vendor/xiaomi"),
]

ALLOW = re.compile(
    r"(sm8250-xiaomi|xiaomi-sm8250|qcom-sm8250|sm8250|kona|umi|cmi|lmi|apollo|alioth|thyme|psyche|cas|munch|elish|enuma|dagu|pipa)",
    re.I,
)
DENY = re.compile(r"(rumi|lumia|sony|hdk|mtp|edo|pdx)", re.I)
TOKEN_SPLIT = re.compile(r"[-_./]+")
PREFER = [
    re.compile(r"^sm8250-xiaomi-[a-z0-9_-]+\.dtb$", re.I),
    re.compile(r"^[a-z0-9_-]+-sm8250\.dtb$", re.I),
    re.compile(r"^qcom-sm8250-[a-z0-9_-]+\.dtb$", re.I),
    re.compile(r"^xiaomi-sm8250-common\.dtb$", re.I),
]


def to_dtb_name(path_str: str) -> str | None:
    p = Path(path_str.strip())
    name = p.name
    if not name.endswith(".dts"):
        return None
    stem = name[:-4]
    if not ALLOW.search(stem) or DENY.search(stem):
        return None
    return stem + ".dtb"


def alias_names(path_str: str, supported_devices: list[str]) -> list[str]:
    raw = path_str.strip().replace("`", "")
    stem = Path(raw).stem.lower()
    tokens = {x for x in TOKEN_SPLIT.split(raw.lower()) if x}
    names: list[str] = []

    for device in supported_devices:
        if device in tokens or stem == device or stem.endswith(f"-{device}"):
            names.extend(
                [
                    f"sm8250-xiaomi-{device}.dtb",
                    f"{device}-sm8250.dtb",
                    f"qcom-sm8250-{device}.dtb",
                ]
            )

    if {"xiaomi", "sm8250"}.issubset(tokens):
        names.append("xiaomi-sm8250-common.dtb")

    seen: set[str] = set()
    out: list[str] = []
    for name in names:
        if name not in seen and not DENY.search(name):
            seen.add(name)
            out.append(name)
    return out


def rank_name(name: str) -> int:
    for i, pattern in enumerate(PREFER):
        if pattern.search(name):
            return i
    return len(PREFER)


def collect_from_logs(
    supported_devices: list[str],
) -> tuple[list[str], list[str], list[str]]:
    names: list[str] = []
    debug: list[str] = []
    used_sources: list[str] = []
    for origin, path in LOG_SOURCES:
        if not path.exists():
            continue
        used_sources.append(origin)
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            raw = line.strip()
            if not raw:
                continue
            primary = to_dtb_name(raw)
            if primary:
                names.append(primary)
                debug.append(f"{origin}\tprimary\t{raw}\t{primary}")
            for alias in alias_names(raw, supported_devices):
                names.append(alias)
                debug.append(f"{origin}\talias\t{raw}\t{alias}")
    return names, debug, used_sources


def collect_from_target_tree(
    supported_devices: list[str],
) -> tuple[list[str], list[str]]:
    names: list[str] = []
    debug: list[str] = []
    for root in TARGET_DTS_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.dts"):
            raw = str(path)
            primary = to_dtb_name(raw)
            if primary:
                names.append(primary)
                debug.append(f"target_tree\tprimary\t{raw}\t{primary}")
            for alias in alias_names(raw, supported_devices):
                names.append(alias)
                debug.append(f"target_tree\talias\t{raw}\t{alias}")
    return names, debug


def fallback_device_candidates(device: str) -> list[str]:
    if not device:
        return []
    return [
        f"sm8250-xiaomi-{device}.dtb",
        f"{device}-sm8250.dtb",
        f"qcom-sm8250-{device}.dtb",
    ]


def resolve_device(config: dict) -> str:
    run_meta = parse_kv(Path("artifacts/run-meta.txt"))
    meta_device = run_meta.get("device", "").strip()
    if meta_device.lower() in {"", "unknown", "?", "n/a"}:
        meta_device = ""
    return (
        (os.getenv("DEVICE", "") or "").strip()
        or meta_device
        or get_nested(config, "reference_baseline_device")
    )


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    config = load_port_config()
    supported_devices = get_supported_devices(config)
    device = resolve_device(config)

    names, debug, log_sources = collect_from_logs(supported_devices)
    source = ",".join(log_sources) if log_sources else ""

    if not names:
        tree_names, tree_debug = collect_from_target_tree(supported_devices)
        names.extend(tree_names)
        debug.extend(tree_debug)
        if tree_names:
            source = "target_dts_scan"

    if not names:
        for candidate in fallback_device_candidates(device):
            names.append(candidate)
            debug.append(f"device_hint\tfallback\t{device}\t{candidate}")
        if names:
            source = "device_hint"

    seen: set[str] = set()
    uniq: list[str] = []
    for name in names:
        if name not in seen:
            seen.add(name)
            uniq.append(name)

    uniq.sort(key=lambda item: (rank_name(item), item))

    OUT.write_text("\n".join(uniq) + ("\n" if uniq else ""), encoding="utf-8")
    debug_lines = [
        f"source={source or 'none'}",
        f"device={device or 'unknown'}",
        f"candidate_total={len(names)}",
        f"unique_total={len(uniq)}",
        "format=origin<TAB>kind<TAB>input<TAB>candidate",
    ]
    debug_lines.extend(debug)
    DEBUG_OUT.write_text("\n".join(debug_lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(uniq)} names, source={source or 'none'})")
    print(f"wrote {DEBUG_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
