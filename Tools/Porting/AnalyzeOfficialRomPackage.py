#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import struct
import zipfile
from pathlib import Path

DEFAULT_ROM_ZIP = Path(r"D:\GIT\MIUI_UMI_OS1.0.5.0.TJBCNXM_d01651ed86_13.0.zip")
DEFAULT_ROM_DIR = Path(r"D:\GIT\MIUI_UMI")
OUT_MD = Path("Porting/OfficialRomAnalysis.md")
OUT_BASELINE = Path("artifacts/official-rom-baseline.json")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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
        lines.append(
            f"- header_version_guess (legacy offset): `{header_version_guess}`"
        )
    else:
        lines.append("- boot magic is not ANDROID! (unexpected for standard boot.img)")
    return lines


def write_missing_report(expected_zip: Path, expected_dir: Path) -> None:
    lines = [
        "# Official ROM Package Analysis (UMI OS1.0.5.0.TJBCNXM)",
        "",
        "## Status",
        "- status: `missing_source_package`",
        f"- expected_zip: `{expected_zip}`",
        f"- expected_dir: `{expected_dir}`",
        "- note: local ROM package/directory not found in current environment; generated placeholder report for CI continuity.",
        "",
        "## Integration Recommendations",
        "1. Provide `OFFICIAL_ROM_DIR` pointing at a local extracted ROM directory when local validation is required.",
        "2. Keep ROM checks as validation-only evidence; do not import proprietary blobs into repository.",
        "3. Until a local ROM source is present, keep ROM consistency items pending in driver integration manifest.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_BASELINE.parent.mkdir(parents=True, exist_ok=True)
    OUT_BASELINE.write_text(
        json.dumps(
            {
                "status": "missing_source_package",
                "expected_zip": str(expected_zip),
                "expected_dir": str(expected_dir),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def resolve_rom_source() -> tuple[Path, str]:
    rom_zip = Path(os.environ.get("OFFICIAL_ROM_ZIP", "") or DEFAULT_ROM_ZIP)
    rom_dir = Path(os.environ.get("OFFICIAL_ROM_DIR", "") or DEFAULT_ROM_DIR)
    if rom_dir.exists() and rom_dir.is_dir():
        return rom_dir, "directory"
    if rom_zip.exists() and rom_zip.is_file():
        return rom_zip, "zip"
    return rom_dir if os.environ.get("OFFICIAL_ROM_DIR") else rom_zip, "missing"


def collect_from_directory(root: Path) -> dict[str, object]:
    files = sorted([p for p in root.rglob("*") if p.is_file()])
    names = [p.relative_to(root).as_posix() for p in files]
    top_dirs = sorted({n.split("/")[0] for n in names if n})
    file_map = {p.relative_to(root).as_posix(): p for p in files}

    def read_text(name: str) -> str:
        path = file_map.get(name)
        if not path:
            return ""
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    def read_bytes(name: str) -> bytes:
        path = file_map.get(name)
        if not path:
            return b""
        try:
            return path.read_bytes()
        except Exception:
            return b""

    return {
        "source": root,
        "source_kind": "directory",
        "source_size": 0,
        "source_sha256": "directory",
        "names": names,
        "top_dirs": top_dirs,
        "metadata_txt": read_text("META-INF/com/android/metadata"),
        "dyn_ops_txt": read_text("dynamic_partitions_op_list"),
        "updater_txt": read_text("META-INF/com/google/android/updater-script"),
        "boot_data": read_bytes("boot.img"),
        "read_bytes": read_bytes,
    }


def collect_from_zip(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as zf:
        infos = zf.infolist()
        names = [i.filename for i in infos]
        top_dirs = sorted({n.split("/")[0] for n in names if n})
        metadata_txt = (
            zf.read("META-INF/com/android/metadata").decode("utf-8", "ignore")
            if "META-INF/com/android/metadata" in names
            else ""
        )
        dyn_ops_txt = (
            zf.read("dynamic_partitions_op_list").decode("utf-8", "ignore")
            if "dynamic_partitions_op_list" in names
            else ""
        )
        updater_txt = (
            zf.read("META-INF/com/google/android/updater-script").decode(
                "utf-8", "ignore"
            )
            if "META-INF/com/google/android/updater-script" in names
            else ""
        )
        blob_cache = {name: zf.read(name) for name in names if not name.endswith("/")}

    return {
        "source": path,
        "source_kind": "zip",
        "source_size": path.stat().st_size,
        "source_sha256": sha256_file(path),
        "names": names,
        "top_dirs": top_dirs,
        "metadata_txt": metadata_txt,
        "dyn_ops_txt": dyn_ops_txt,
        "updater_txt": updater_txt,
        "boot_data": blob_cache.get("boot.img", b""),
        "read_bytes": blob_cache.get,
    }


def main() -> int:
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)

    source, source_kind = resolve_rom_source()
    if source_kind == "missing":
        write_missing_report(DEFAULT_ROM_ZIP, DEFAULT_ROM_DIR)
        print(f"Wrote {OUT_MD} (source package missing)")
        return 0

    data = (
        collect_from_directory(source)
        if source_kind == "directory"
        else collect_from_zip(source)
    )
    names = data["names"]
    top_dirs = data["top_dirs"]
    metadata_txt = data["metadata_txt"]
    dyn_ops_txt = data["dyn_ops_txt"]
    updater_txt = data["updater_txt"]
    boot_data = data["boot_data"]
    read_bytes = data["read_bytes"]

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
    firmware_entries = sorted(
        [n for n in names if n.startswith("firmware-update/") and not n.endswith("/")]
    )

    lines: list[str] = []
    lines.append("# Official ROM Package Analysis (UMI OS1.0.5.0.TJBCNXM)")
    lines.append("")
    lines.append("## Status")
    lines.append("- status: `ok`")
    lines.append(f"- Source Kind: `{source_kind}`")
    lines.append(f"- Source File: `{source}`")
    if source_kind == "zip":
        lines.append(f"- Zip Size Bytes: `{data['source_size']}`")
        lines.append(f"- Zip SHA256: `{data['source_sha256']}`")
    lines.append(f"- Entry Count: `{len(names)}`")
    lines.append(f"- Top-Level Entries: `{', '.join(top_dirs)}`")
    lines.append("")

    lines.append("## Package Metadata")
    if str(metadata_txt).strip():
        lines.append("```text")
        lines.extend(str(metadata_txt).strip().splitlines())
        lines.append("```")
    else:
        lines.append("- metadata file missing or unreadable")
    lines.append("")

    lines.append("## Dynamic Partitions Operation List")
    if str(dyn_ops_txt).strip():
        lines.append("```text")
        lines.extend(str(dyn_ops_txt).strip().splitlines()[:200])
        lines.append("```")
    else:
        lines.append("- dynamic_partitions_op_list missing or unreadable")
    lines.append("")

    lines.append("## Updater Script (Key Excerpt)")
    if str(updater_txt).strip():
        lines.append("```text")
        lines.extend(str(updater_txt).strip().splitlines()[:220])
        lines.append("```")
    else:
        lines.append("- updater-script missing or unreadable")
    lines.append("")

    lines.append("## Firmware Payload Snapshot")
    lines.append(f"- firmware-update entries: `{len(firmware_entries)}`")
    lines.append(
        "- sample: "
        + (", ".join(firmware_entries[:25]) if firmware_entries else "(none)")
    )
    lines.append("")

    lines.append("## Key Image/Data Entries")
    for k in key_files:
        blob = read_bytes(k)
        if blob:
            lines.append(f"- `{k}`: size=`{len(blob)}` sha256=`{sha256_bytes(blob)}`")
        else:
            lines.append(f"- `{k}`: (not present)")
    lines.append("")

    if boot_data:
        lines.append("## boot.img Header Snapshot")
        lines.extend(boot_header_summary(boot_data))
        lines.append("")

    lines.append("## Integration Recommendations (Moderate)")
    lines.append(
        "1. Treat this package as baseline evidence only; do not directly import proprietary blobs into the repository."
    )
    lines.append(
        "2. Keep using extracted metadata + partition ops + hash evidence for reproducibility and regression tracking."
    )
    lines.append(
        "3. Compare boot/dtbo/vbmeta hashes against CI-generated artifacts to validate release-chain consistency."
    )
    lines.append(
        "4. Continue kernel-side integration via open-source references; use the local official ROM package/directory as validation target, not code donor."
    )

    baseline = {
        "status": "ok",
        "source_file": str(source),
        "source_kind": source_kind,
        "bootimg": {
            "size": len(boot_data),
            "sha256": sha256_bytes(boot_data) if boot_data else "",
            "header_version_guess": struct.unpack("<I", boot_data[40:44])[0]
            if len(boot_data) >= 44
            else 0,
        },
        "firmware": {
            name: {
                "size": len(read_bytes(name)),
                "sha256": sha256_bytes(read_bytes(name)),
            }
            for name in [
                "firmware-update/dtbo.img",
                "firmware-update/vbmeta.img",
                "firmware-update/vbmeta_system.img",
            ]
            if read_bytes(name)
        },
    }
    OUT_BASELINE.parent.mkdir(parents=True, exist_ok=True)
    OUT_BASELINE.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_BASELINE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
