#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFCONFIG = ROOT / "arch" / "arm64" / "configs" / "umi_defconfig"
DTS = ROOT / "arch" / "arm64" / "boot" / "dts" / "qcom" / "sm8250-xiaomi-umi.dts"
DTS_MAKEFILE = ROOT / "arch" / "arm64" / "boot" / "dts" / "qcom" / "Makefile"
VDSO_DIR = ROOT / "arch" / "arm64" / "kernel" / "vdso"
VDSO32_DIR = ROOT / "arch" / "arm64" / "kernel" / "vdso32"
SYSCALL_64_TABLE = ROOT / "arch" / "arm64" / "tools" / "syscall_64.tbl"
BUILD_INPUTS = [
    ROOT / "scripts" / "module.lds.S",
    ROOT / "usr" / "initramfs_data.S",
    ROOT / "certs" / "system_certificates.S",
    ROOT / "arch" / "arm64" / "kernel" / "vmlinux.lds.S",
    ROOT / "arch" / "arm64" / "kernel" / "entry.S",
    ROOT / "arch" / "arm64" / "lib" / "clear_page.S",
    ROOT / "arch" / "arm64" / "mm" / "cache.S",
    ROOT / "arch" / "arm64" / "kvm" / "hyp" / "entry.S",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not (ROOT / "arch" / "arm64").exists():
        print("umi build target selftest=skipped (kernel source not present)")
        return 0

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

    for name in ["vdso.lds.S", "note.S", "sigreturn.S", "vgetrandom-chacha.S"]:
        require((VDSO_DIR / name).is_file(), f"missing arm64 vdso source: {name}")

    require((VDSO32_DIR / "vdso.lds.S").is_file(), "missing arm64 compat vdso linker script")

    vdso_linker = (VDSO_DIR / "vdso.lds.S").read_text(encoding="utf-8", errors="ignore")
    require("_vdso_rng_data" in vdso_linker, "arm64 vdso linker script must expose RNG data")
    require("__kernel_getrandom" in vdso_linker, "arm64 vdso linker script must export getrandom")

    syscall_64_table = SYSCALL_64_TABLE.read_text(encoding="utf-8", errors="ignore")
    require("getrandom" in syscall_64_table, "arm64 syscall_64.tbl must resolve to syscall table content")

    for build_input in BUILD_INPUTS:
        require(build_input.is_file(), f"missing kernel build input: {build_input.relative_to(ROOT)}")

    print("umi build target selftest=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
