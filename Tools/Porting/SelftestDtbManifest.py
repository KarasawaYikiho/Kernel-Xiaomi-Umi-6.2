#!/usr/bin/env python3
from __future__ import annotations

from BuildDtbManifest import alias_names, to_dtb_name


SUPPORTED = [
    "alioth",
    "apollo",
    "cas",
    "cmi",
    "dagu",
    "elish",
    "enuma",
    "lmi",
    "munch",
    "pipa",
    "psyche",
    "thyme",
    "umi",
]


def expect_equal(name: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")


def expect_not_in(name: str, needle: str, haystack: list[str]) -> None:
    if needle in haystack:
        raise AssertionError(f"{name}: unexpected {needle!r} in {haystack!r}")


def main() -> int:
    expect_equal(
        "iot_rb5_primary_is_not_phase2_required",
        to_dtb_name("arch/arm64/boot/dts/qcom/kona-v2.1-iot-rb5.dts"),
        None,
    )
    aliases = alias_names(
        "source/arch/arm64/boot/dts/vendor/qcom/umi-sm8250-overlay.dts",
        SUPPORTED,
    )
    expect_equal(
        "umi_overlay_aliases",
        aliases,
        ["sm8250-xiaomi-umi.dtb", "umi-sm8250.dtb", "qcom-sm8250-umi.dtb"],
    )
    expect_not_in("umi_overlay_no_common_dtb", "xiaomi-sm8250-common.dtb", aliases)
    print("dtb manifest filters non-device blockers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
