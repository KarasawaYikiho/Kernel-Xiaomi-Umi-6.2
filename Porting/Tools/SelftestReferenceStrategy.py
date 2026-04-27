#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def expect(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)


def load_config() -> dict:
    return json.loads((ROOT / "Porting" / "Sm8250PortConfig.json").read_text(encoding="utf-8"))


def test_reference_sources_are_registered() -> None:
    config = load_config()
    refs = config.get("reference_sources", [])
    by_name = {item.get("name", ""): item for item in refs}

    expect("LineageOS source registered", "LineageOSSm8250" in by_name)
    expect("Liyafe source registered", "LiyafeSm8250Mod" in by_name)
    expect("N0Kernel source registered", "N0KernelUmiAnyKernel" in by_name)

    expect("LineageOS is donor candidate", by_name["LineageOSSm8250"].get("role") == "targeted_donor_candidate")
    expect("Liyafe is cautious donor", by_name["LiyafeSm8250Mod"].get("role") == "cautious_targeted_donor_candidate")
    expect("N0Kernel is packaging reference", by_name["N0KernelUmiAnyKernel"].get("role") == "packaging_reference")

    for name in ("LineageOSSm8250", "LiyafeSm8250Mod"):
        source = by_name[name]
        expect(f"{name} kernel version", source.get("kernel_version") == "4.19.325")
        expect(f"{name} has umi relevance", "umi" in source.get("relevance", []))
        expect(f"{name} is not primary base", source.get("primary_base") is False)


def test_boot_strategy_is_patcher_agnostic() -> None:
    config = load_config()
    boot = config.get("boot_artifact_strategy", {})
    expect("boot strategy kind", boot.get("kind") == "official_aligned_custom_boot")
    expect("boot strategy first route", boot.get("first_device_route") == "fastboot_boot")
    patchers = set(boot.get("compatible_patchers", []))
    expect("KernelSU compatible", "KernelSU" in patchers)
    expect("Magisk compatible", "Magisk" in patchers)
    expect("strategy patcher agnostic", boot.get("patcher_agnostic") is True)


def test_reference_strategy_document_is_consistent() -> None:
    doc = ROOT / "Porting" / "ReferenceSourceStrategy.md"
    expect("reference strategy document exists", doc.exists())
    text = doc.read_text(encoding="utf-8", errors="ignore")
    for required in [
        "yefxx 6.11 remains the experimental mainline build baseline",
        "LineageOS/android_kernel_xiaomi_sm8250",
        "liyafe1997/kernel_xiaomi_sm8250_mod",
        "N0Kernel-umi-2024-12-30_23-10-52.zip",
        "official-aligned custom boot",
        "KernelSU",
        "Magisk",
        "No blind subtree copy",
    ]:
        expect(f"reference strategy mentions {required}", required in text)


def main() -> int:
    tests = [
        test_reference_sources_are_registered,
        test_boot_strategy_is_patcher_agnostic,
        test_reference_strategy_document_is_consistent,
    ]
    for test in tests:
        test()
    print("reference-strategy-selftest=ok")
    print(f"case_count={len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
