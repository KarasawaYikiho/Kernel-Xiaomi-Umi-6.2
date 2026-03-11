import hashlib
import struct
import zipfile
from pathlib import Path

ROM_ZIP = Path(r"D:\GIT\MIUI_UMI_OS1.0.5.0.TJBCNXM_d01651ed86_13.0.zip")
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


def main() -> int:
    if not ROM_ZIP.exists():
        raise FileNotFoundError(f"ROM zip not found: {ROM_ZIP}")

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

        lines: list[str] = []
        lines.append("# Official ROM Package Analysis (UMI OS1.0.5.0.TJBCNXM)")
        lines.append("")
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
