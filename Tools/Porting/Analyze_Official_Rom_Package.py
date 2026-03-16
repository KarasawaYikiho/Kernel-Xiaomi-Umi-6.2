#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import os
import struct
import zipfile
from pathlib import Path

DEFAULT_ROM_PATH = r"D:\GIT\MIUI_UMI_OS1.0.5.0.TJBCNXM_d01651ed86_13.0.zip"
ROM_ZIP = Path(os.environ.get("OFFICIAL_ROM_ZIP", DEFAULT_ROM_PATH))
OUT_MD = Path("Porting/OfficialRom-Umi-Os1.0.5.0-Analysis.md")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(zf: zipfile.ZipFile, name: str) -> str:
    try:
        return zf.read(name).decode("utf-8", "ignore")
    except Exception:
        return ""


def boot_header_summary(boot: bytes) -> list[str]:
    lines: list[str] = []
    if len(boot) < 64:
        return ["- boot header: too small"]
    magic = boot[:8]
    lines.append(f"- boot magic: `{magic!r}`")
    if magic == b"ANDROID!":
        kernel_size = struct.unpack("<I", boot[8:12])[0]
        ramdisk_size = struct.unpack("<I", boot[16:20])[0]
        header_version_guess = struct.unpack("<I", boot[40:44])[0]
        lines.append(f"- kernel_size (legacy offset): `{kernel_size}`")
        lines.append(f"- ramdisk_size (legacy offset): `{ramdisk_size}`")
        lines.append(f"- header_version_guess (legacy offset): `{header_version_guess}`")
    else:
        lines.append("- boot magic is not ANDROID! (unexpected for standard boot.img)")
    return lines


def write_missing_report(path: Path) -> None:
    lines: list[str] = []
    lines.append("# Official ROM Package Analysis (UMI OS1.0.5.0.TJBCNXM)")
    lines.append("")
    lines.append("## Status")
    lines.append("- status: `missing_source_package`")
    lines.append(f"- expected_source: `{path}`")
    lines.append("- note: ROM package not found in current environment; generated placeholder report for CI continuity.")
    lines.append("")
    lines.append("## Integration Recommendations")
    lines.append("1. Provide OFFICIAL_ROM_ZIP path in local/CI runtime when ROM baseline validation is required.")
    lines.append("2. Keep ROM checks as validation-only evidence; do not import proprietary blobs into repository.")
    lines.append("3. Until ROM package is present, keep ROM consistency items pending in driver integration manifest.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    if not ROM_ZIP.exists():
        write_missing_report(ROM_ZIP)
        print(f"Wrote {OUT_MD} (source package missing)")
        return 0

    with zipfile.ZipFile(ROM_ZIP) as zf:
        infos = zf.infolist()
        names = [i.filename for i in infos]
        top_dirs = sorted({n.split("/")[0] for n in names if n})

        metadata_txt = read_text(zf, "META-INF/com/android/metadata")
        dyn_ops_txt = read_text(zf, "dynamic_partitions_op_list")
        updater_txt = read_text(zf, "META-INF/com/google/android/updater-script")

        key_files = [
            "boot.img",
            "firmware-update/dtbo.img",
            "firmware-update/vbmeta.img",
            "firmware-update/vbmeta_system.img",
            "system.new.dat.br",
            "vendor.new.dat.br",
            "product.new.dat.br",
            "odm.new.dat.br",
            "system_ext.new.dat.br",
            "mi_ext.new.dat.br",
        ]
        firmware_entries = sorted([n for n in names if n.startswith("firmware-update/") and not n.endswith("/")])

        lines: list[str] = []
        lines.append("# Official ROM Package Analysis (UMI OS1.0.5.0.TJBCNXM)")
        lines.append("")
        lines.append("## Status")
        lines.append("- status: `ok`")
        lines.append(f"- Source File: `{ROM_ZIP}`")
        lines.append(f"- Zip Size Bytes: `{ROM_ZIP.stat().st_size}`")
        lines.append(f"- Zip SHA256: `{sha256_bytes(ROM_ZIP.read_bytes())}`")
        lines.append(f"- Entry Count: `{len(infos)}`")
        lines.append(f"- Top-Level Entries: `{', '.join(top_dirs)}`")
        lines.append("")

        lines.append("## Package Metadata")
        if metadata_txt.strip():
            lines.append("```text")
            lines.extend(metadata_txt.strip().splitlines())
            lines.append("```")
        else:
            lines.append("- metadata file missing or unreadable")
        lines.append("")

        lines.append("## Dynamic Partitions Operation List")
        if dyn_ops_txt.strip():
            lines.append("```text")
            lines.extend(dyn_ops_txt.strip().splitlines()[:200])
            lines.append("```")
        else:
            lines.append("- dynamic_partitions_op_list missing or unreadable")
        lines.append("")

        lines.append("## Updater Script (Key Excerpt)")
        if updater_txt.strip():
            lines.append("```text")
            lines.extend(updater_txt.strip().splitlines()[:220])
            lines.append("```")
        else:
            lines.append("- updater-script missing or unreadable")
        lines.append("")

        lines.append("## Firmware Payload Snapshot")
        lines.append(f"- firmware-update entries: `{len(firmware_entries)}`")
        lines.append("- sample: " + (", ".join(firmware_entries[:25]) if firmware_entries else "(none)"))
        lines.append("")

        lines.append("## Key Image/Data Entries")
        for k in key_files:
            if k in names:
                data = zf.read(k)
                lines.append(f"- `{k}`: size=`{len(data)}` sha256=`{sha256_bytes(data)}`")
            else:
                lines.append(f"- `{k}`: (not present)")
        lines.append("")

        if "boot.img" in names:
            boot = zf.read("boot.img")
            lines.append("## boot.img Header Snapshot")
            lines.extend(boot_header_summary(boot))
            lines.append("")

        lines.append("## Integration Recommendations (Moderate)")
        lines.append("1. Treat this package as baseline evidence only; do not directly import proprietary blobs into the repository.")
        lines.append("2. Keep using extracted metadata + partition ops + hash evidence for reproducibility and regression tracking.")
        lines.append("3. Compare boot/dtbo/vbmeta hashes against CI-generated artifacts to validate release-chain consistency.")
        lines.append("4. Continue kernel-side integration via open-source references; use official ROM package as validation target, not code donor.")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
