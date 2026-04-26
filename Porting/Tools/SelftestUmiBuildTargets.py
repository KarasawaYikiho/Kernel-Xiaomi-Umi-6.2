#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFCONFIG = ROOT / "arch" / "arm64" / "configs" / "umi_defconfig"
DTS = ROOT / "arch" / "arm64" / "boot" / "dts" / "qcom" / "sm8250-xiaomi-umi.dts"
DTS_MAKEFILE = ROOT / "arch" / "arm64" / "boot" / "dts" / "qcom" / "Makefile"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    require(DEFCONFIG.is_file(), "missing arch/arm64/configs/umi_defconfig")
    require(DTS.is_file(), "missing arch/arm64/boot/dts/qcom/sm8250-xiaomi-umi.dts")

    defconfig = DEFCONFIG.read_text(encoding="utf-8", errors="ignore")
    require("CONFIG_ARCH_QCOM=y" in defconfig, "umi_defconfig must enable ARCH_QCOM")

    dts = DTS.read_text(encoding="utf-8", errors="ignore")
    require('model = "Xiaomi Mi 10";' in dts, "DTS must identify Xiaomi Mi 10")
    require('compatible = "xiaomi,umi", "qcom,sm8250";' in dts, "DTS must use umi/sm8250 compatibles")
    require('#include "sm8250.dtsi"' in dts, "DTS must include sm8250.dtsi")

    makefile = DTS_MAKEFILE.read_text(encoding="utf-8", errors="ignore")
    require("sm8250-xiaomi-umi.dtb" in makefile, "QCOM DTS Makefile must build sm8250-xiaomi-umi.dtb")

    print("umi build target selftest=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
