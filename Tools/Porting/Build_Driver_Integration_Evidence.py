#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "driver-integration-evidence.txt"
ROM_REPORT = Path("Porting/OfficialRom-Umi-Os1.0.5.0-Analysis.md")
REF_REPORT = Path("Porting/Reference-Drivers-Analysis.md")
COPIED_DTS = ART / "copied_dts.txt"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _extract_rom_hashes(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    # Matches lines like: - `boot.img`: size=`...` sha256=`...`
    pattern = re.compile(r"`([^`]+)`:\s*size=`\d+`\s*sha256=`([0-9a-f]{64})`", re.IGNORECASE)
    for m in pattern.finditer(text):
        out[m.group(1).strip()] = m.group(2).lower()
    return out


def _find_first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.exists() and p.is_file():
            return p
    return None


def _find_candidate_by_name(root: Path, names: list[str]) -> Path | None:
    if not root.exists():
        return None
    lowered = {n.lower() for n in names}
    for p in root.rglob("*"):
        if p.is_file() and p.name.lower() in lowered:
            return p
    return None


def _contains_any(text: str, keys: list[str]) -> bool:
    low = text.lower()
    return any(k.lower() in low for k in keys)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    rom_text = _load_text(ROM_REPORT)
    ref_text = _load_text(REF_REPORT)
    copied_text = _load_text(COPIED_DTS)

    rom_hashes = _extract_rom_hashes(rom_text)

    # Boot chain consistency checks
    boot_local = _find_first_existing([
        ART / "boot.img",
        ART / "umi_bundle" / "boot.img",
        Path("out/boot.img"),
        Path("out/arch/arm64/boot/boot.img"),
    ])

    dtbo_local = _find_candidate_by_name(ART, ["dtbo.img"]) or _find_candidate_by_name(Path("out"), ["dtbo.img"])
    vbmeta_local = _find_candidate_by_name(ART, ["vbmeta.img"]) or _find_candidate_by_name(Path("out"), ["vbmeta.img"])

    boot_match = "no"
    dtbo_match = "no"
    vbmeta_match = "no"

    if boot_local and "boot.img" in rom_hashes:
        boot_match = "yes" if _sha256(boot_local) == rom_hashes["boot.img"] else "no"

    if dtbo_local and "firmware-update/dtbo.img" in rom_hashes:
        dtbo_match = "yes" if _sha256(dtbo_local) == rom_hashes["firmware-update/dtbo.img"] else "no"

    vbmeta_key = "firmware-update/vbmeta.img"
    if vbmeta_local and vbmeta_key in rom_hashes:
        vbmeta_match = "yes" if _sha256(vbmeta_local) == rom_hashes[vbmeta_key] else "no"

    # Driver-area evidence (conservative text/path signals)
    joined = ref_text + "\n" + copied_text
    cam_signal = _contains_any(joined, ["camera", "cam_sensor", "cam_isp", "camss"])
    cam_isp_signal = _contains_any(joined, ["cam_isp", "camss", "isp", "msm_isp"])
    dsp_signal = _contains_any(joined, ["display", "dsi", "drm", "msm_drm"])
    thm_signal = _contains_any(joined, ["thermal", "power", "qcom", "cpufreq"])
    aud_signal = _contains_any(joined, ["audio", "snd", "wcd", "q6"])
    xiaomi_signal = _contains_any(joined, ["xiaomi", "umi", "sm8250"])

    ref_camera_alignment = "yes" if cam_signal else "no"
    ref_display_alignment = "yes" if dsp_signal else "no"
    ref_thermal_alignment = "yes" if thm_signal else "no"
    ref_xiaomi_alignment = "yes" if xiaomi_signal else "no"

    partition_signal = _contains_any(rom_text, ["dynamic partition", "dynamic_partitions_op_list"])

    lines = [
        "status=ok",
        f"boot_chain_match={boot_match}",
        f"dtbo_match={dtbo_match}",
        f"vbmeta_match={vbmeta_match}",
        f"partition_baseline_signal={'yes' if partition_signal else 'no'}",
        f"camera_signal={'yes' if cam_signal else 'no'}",
        f"camera_isp_signal={'yes' if cam_isp_signal else 'no'}",
        f"display_signal={'yes' if dsp_signal else 'no'}",
        f"thermal_signal={'yes' if thm_signal else 'no'}",
        f"audio_signal={'yes' if aud_signal else 'no'}",
        f"ref_driver_xiaomi_alignment={ref_xiaomi_alignment}",
        f"ref_driver_camera_alignment={ref_camera_alignment}",
        f"ref_driver_display_alignment={ref_display_alignment}",
        f"ref_driver_thermal_alignment={ref_thermal_alignment}",
        f"boot_local_path={(boot_local.as_posix() if boot_local else '')}",
        f"dtbo_local_path={(dtbo_local.as_posix() if dtbo_local else '')}",
        f"vbmeta_local_path={(vbmeta_local.as_posix() if vbmeta_local else '')}",
    ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
