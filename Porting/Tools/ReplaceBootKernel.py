#!/usr/bin/env python3
from __future__ import annotations

import argparse
import struct
from pathlib import Path


ANDROID_MAGIC = b"ANDROID!"
PAGE_SIZE_OFFSET = 36
HEADER_VERSION_OFFSET = 40
KERNEL_SIZE_OFFSET = 8
RAMDISK_SIZE_OFFSET = 16
SECOND_SIZE_OFFSET = 24
RECOVERY_DTBO_SIZE_OFFSET = 1632
RECOVERY_DTBO_OFFSET_OFFSET = 1636
HEADER_SIZE_OFFSET = 1644
DTB_SIZE_OFFSET = 1648


def align(value: int, page_size: int) -> int:
    return ((value + page_size - 1) // page_size) * page_size


def u32(data: bytes | bytearray, offset: int) -> int:
    if len(data) < offset + 4:
        return 0
    return struct.unpack_from("<I", data, offset)[0]


def section(data: bytes, offset: int, size: int) -> bytes:
    if size <= 0:
        return b""
    end = offset + size
    if end > len(data):
        raise ValueError(f"boot image section exceeds file size at {offset}:{end}")
    return data[offset:end]


def replace_boot_kernel(
    stock_boot: Path,
    kernel_image: Path,
    output_boot: Path,
    *,
    required_bytes: int = 0,
) -> None:
    original = stock_boot.read_bytes()
    if not original.startswith(ANDROID_MAGIC):
        raise ValueError(f"not an Android boot image: {stock_boot}")

    page_size = u32(original, PAGE_SIZE_OFFSET)
    if page_size <= 0:
        raise ValueError("boot image has invalid page size")
    header_version = u32(original, HEADER_VERSION_OFFSET)
    if header_version > 2:
        raise ValueError(f"unsupported boot header version: {header_version}")

    kernel_size = u32(original, KERNEL_SIZE_OFFSET)
    ramdisk_size = u32(original, RAMDISK_SIZE_OFFSET)
    second_size = u32(original, SECOND_SIZE_OFFSET)
    recovery_dtbo_size = u32(original, RECOVERY_DTBO_SIZE_OFFSET) if header_version >= 1 else 0
    dtb_size = u32(original, DTB_SIZE_OFFSET) if header_version >= 2 else 0

    kernel_offset = page_size
    ramdisk_offset = kernel_offset + align(kernel_size, page_size)
    second_offset = ramdisk_offset + align(ramdisk_size, page_size)
    recovery_dtbo_offset = second_offset + align(second_size, page_size)
    dtb_offset = recovery_dtbo_offset + align(recovery_dtbo_size, page_size)

    ramdisk = section(original, ramdisk_offset, ramdisk_size)
    second = section(original, second_offset, second_size)
    recovery_dtbo = section(original, recovery_dtbo_offset, recovery_dtbo_size)
    dtb = section(original, dtb_offset, dtb_size)

    new_kernel = kernel_image.read_bytes()
    if not new_kernel:
        raise ValueError(f"kernel image is empty: {kernel_image}")

    header = bytearray(original[:page_size])
    struct.pack_into("<I", header, KERNEL_SIZE_OFFSET, len(new_kernel))
    if header_version >= 1:
        struct.pack_into("<Q", header, RECOVERY_DTBO_OFFSET_OFFSET, 0)

    out = bytearray(header)
    for payload in (new_kernel, ramdisk, second, recovery_dtbo, dtb):
        if payload:
            out.extend(payload)
        out.extend(b"\0" * (align(len(out), page_size) - len(out)))

    if required_bytes > 0:
        if len(out) > required_bytes:
            raise ValueError(
                f"repacked boot image exceeds required size: {len(out)} > {required_bytes}"
            )
        out.extend(b"\0" * (required_bytes - len(out)))

    output_boot.parent.mkdir(parents=True, exist_ok=True)
    output_boot.write_bytes(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stock-boot", required=True)
    parser.add_argument("--kernel", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--required-bytes", type=int, default=0)
    args = parser.parse_args()
    replace_boot_kernel(
        Path(args.stock_boot),
        Path(args.kernel),
        Path(args.output),
        required_bytes=args.required_bytes,
    )
    print(Path(args.output).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
