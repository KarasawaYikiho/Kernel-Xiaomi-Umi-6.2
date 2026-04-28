#!/usr/bin/env python3
from __future__ import annotations

import struct
import tempfile
from pathlib import Path
import os
import hashlib

import ReplaceBootKernel
import ValidateBootImage


ANDROID_MAGIC = b"ANDROID!"


def align(value: int, page_size: int) -> int:
    return ((value + page_size - 1) // page_size) * page_size


def make_boot_v2(path: Path, kernel: bytes, ramdisk: bytes, dtb: bytes) -> None:
    page_size = 4096
    header_size = 1660
    header = bytearray(page_size)
    struct.pack_into("<8s10I16s512s32s1024sIQIIQ", header, 0,
        ANDROID_MAGIC,
        len(kernel),
        0x8000,
        len(ramdisk),
        0x01000000,
        0,
        0,
        0x100,
        page_size,
        2,
        0,
        b"umi-test",
        b"console=ttyMSM0",
        b"0" * 32,
        b"",
        0,
        0,
        header_size,
        len(dtb),
        0x01F00000,
    )
    blob = bytearray(header)
    blob.extend(kernel)
    blob.extend(b"\0" * (align(len(blob), page_size) - len(blob)))
    blob.extend(ramdisk)
    blob.extend(b"\0" * (align(len(blob), page_size) - len(blob)))
    blob.extend(dtb)
    blob.extend(b"\0" * (align(len(blob), page_size) - len(blob)))
    path.write_bytes(blob)


def expect(name: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")


def kv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" in raw:
            key, value = raw.split("=", 1)
            out[key] = value
    return out


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        stock = tmp / "stock-boot.img"
        out = tmp / "custom-boot.img"
        new_kernel = tmp / "Image.gz"
        make_boot_v2(stock, b"stock-kernel", b"official-ramdisk", b"official-dtb")
        new_kernel.write_bytes(b"custom-kernel-image")

        ReplaceBootKernel.replace_boot_kernel(
            stock,
            new_kernel,
            out,
            required_bytes=stock.stat().st_size,
        )

        data = out.read_bytes()
        expect("size", out.stat().st_size, stock.stat().st_size)
        expect("magic", data[:8], ANDROID_MAGIC)
        expect("kernel size", struct.unpack_from("<I", data, 8)[0], len(b"custom-kernel-image"))
        expect("ramdisk size", struct.unpack_from("<I", data, 16)[0], len(b"official-ramdisk"))
        expect("header version", struct.unpack_from("<I", data, 40)[0], 2)
        expect("dtb size", struct.unpack_from("<I", data, 1648)[0], len(b"official-dtb"))
        if b"custom-kernel-image" not in data:
            raise AssertionError("custom kernel payload missing")
        if b"official-ramdisk" not in data:
            raise AssertionError("official ramdisk payload missing")
        if b"official-dtb" not in data:
            raise AssertionError("official dtb payload missing")

        cwd = Path.cwd()
        old_required_bytes = os.environ.get("BOOTIMG_REQUIRED_BYTES")
        try:
            os.chdir(tmp)
            os.environ["BOOTIMG_REQUIRED_BYTES"] = str(stock.stat().st_size)
            (tmp / "artifacts").mkdir()
            (tmp / "Porting" / "OfficialRomBaseline").mkdir(parents=True)
            (tmp / "artifacts" / "boot.img").write_bytes(data)
            (tmp / "artifacts" / "bootimg-build.txt").write_text(
                "status=ok\nsource=official_rom_repacked_kernel\nsource_ref=stock-boot.img\n",
                encoding="utf-8",
            )
            (tmp / "Porting" / "OfficialRomBaseline" / "BootImageBaseline.env").write_text(
                f"BOOTIMG_REQUIRED_BYTES={stock.stat().st_size}\n"
                "BOOTIMG_HEADER_VERSION=2\n"
                f"ROM_BOOTIMG_SHA256={hashlib.sha256(stock.read_bytes()).hexdigest()}\n",
                encoding="utf-8",
            )
            (tmp / "Porting" / "OfficialRomAnalysis.md").write_text(
                f"- `boot.img`: size=`{stock.stat().st_size}` sha256=`{hashlib.sha256(stock.read_bytes()).hexdigest()}`\n",
                encoding="utf-8",
            )
            ValidateBootImage.main()
            boot_info = kv(tmp / "artifacts" / "bootimg-info.txt")
            expect("validate status", boot_info.get("status"), "ok")
            expect("official reference gate", boot_info.get("official_reference_gate"), "yes")
            expect("stock sha mismatch allowed", boot_info.get("rom_sha256_match"), "no")
        finally:
            if old_required_bytes is None:
                os.environ.pop("BOOTIMG_REQUIRED_BYTES", None)
            else:
                os.environ["BOOTIMG_REQUIRED_BYTES"] = old_required_bytes
            os.chdir(cwd)

    print("boot-image-repack-selftest=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
