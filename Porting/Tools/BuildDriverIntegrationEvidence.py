#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

ART = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
OUT = ART / "driver-integration-evidence.txt"
ROM_REPORT = Path("Porting/OfficialRomAnalysis.md")
REF_REPORT = Path("Porting/ReferenceDriversAnalysis.md")
INVENTORY = Path("Porting/Inventory.json")
COPIED_DTS = ART / "copied_dts.txt"
TARGET = Path(os.getenv("KERNEL_DIR", "."))
ROM_BASELINE_DIR = Path("Porting/OfficialRomBaseline")
ROM_BASELINE_DTBO = ROM_BASELINE_DIR / "Dtbo.img"
ROM_BASELINE_VBMETA = ROM_BASELINE_DIR / "Vbmeta.img"


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
    pattern = re.compile(
        r"`([^`]+)`:\s*size=`\d+`\s*sha256=`([0-9a-f]{64})`", re.IGNORECASE
    )
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


def _path_exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def _load_inventory() -> dict:
    if not INVENTORY.exists():
        return {}
    try:
        return json.loads(INVENTORY.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def _collect_inventory_tokens(inventory: dict) -> str:
    chunks: list[str] = []
    for repo_name, payload in inventory.items():
        if not isinstance(payload, dict):
            continue
        repo = str(payload.get("repo", ""))
        ref = str(payload.get("ref", ""))
        chunks.extend([repo_name, repo, ref])
        for section in (
            "arch/arm64/configs",
            "arch/arm64/boot/dts",
            "techpack",
            "drivers",
        ):
            value = payload.get(section, [])
            if isinstance(value, list):
                chunks.extend(str(x) for x in value)
    return "\n".join(chunks)


def _inventory_list(inventory: dict, repo_key: str, section: str) -> list[str]:
    payload = inventory.get(repo_key, {}) if isinstance(inventory, dict) else {}
    if not isinstance(payload, dict):
        return []
    value = payload.get(section, [])
    if not isinstance(value, list):
        return []
    return [str(x).lower() for x in value]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    rom_text = _load_text(ROM_REPORT)
    ref_text = _load_text(REF_REPORT)
    copied_text = _load_text(COPIED_DTS)
    inventory = _load_inventory()
    inventory_text = _collect_inventory_tokens(inventory)

    rom_hashes = _extract_rom_hashes(rom_text)

    # Boot chain consistency checks
    boot_local = _find_first_existing(
        [
            ART / "boot.img",
            ART / "device_bundle" / "boot.img",
            Path(os.getenv("OUT_DIR", "out")) / "boot.img",
            Path(os.getenv("OUT_DIR", "out")) / "arch/arm64/boot/boot.img",
            ROM_BASELINE_DIR / "boot.img",
        ]
    )

    dtbo_local = (
        _find_candidate_by_name(ART, ["dtbo.img"])
        or _find_candidate_by_name(Path("out"), ["dtbo.img"])
        or _find_first_existing([ROM_BASELINE_DTBO])
    )
    vbmeta_local = (
        _find_candidate_by_name(ART, ["vbmeta.img"])
        or _find_candidate_by_name(Path("out"), ["vbmeta.img"])
        or _find_first_existing([ROM_BASELINE_VBMETA])
    )

    boot_match = "no"
    dtbo_match = "no"
    vbmeta_match = "no"

    if boot_local and "boot.img" in rom_hashes:
        boot_match = "yes" if _sha256(boot_local) == rom_hashes["boot.img"] else "no"

    if dtbo_local and "firmware-update/dtbo.img" in rom_hashes:
        dtbo_match = (
            "yes"
            if _sha256(dtbo_local) == rom_hashes["firmware-update/dtbo.img"]
            else "no"
        )

    vbmeta_key = "firmware-update/vbmeta.img"
    if vbmeta_local and vbmeta_key in rom_hashes:
        vbmeta_match = (
            "yes" if _sha256(vbmeta_local) == rom_hashes[vbmeta_key] else "no"
        )

    # Driver-area evidence
    joined = ref_text + "\n" + copied_text + "\n" + inventory_text
    so_ts_techpack = set(_inventory_list(inventory, "so_ts", "techpack"))
    so_ts_drivers = set(_inventory_list(inventory, "so_ts", "drivers"))
    camera_ref_drivers = set(
        _inventory_list(inventory, "reference_utsav_camera_kernel", "drivers")
    )
    display_ref_repo = (
        str(
            inventory.get("reference_utsav_display_drivers", {}).get("repo", "")
        ).lower()
        if isinstance(inventory.get("reference_utsav_display_drivers", {}), dict)
        else ""
    )

    target_present = TARGET.exists()
    local_camera_paths = [
        "techpack/camera",
        "techpack/camera-xiaomi",
        "drivers/media/platform/msm/camera",
        "drivers/media/platform/qcom/camera",
    ]
    local_display_paths = [
        "techpack/display",
        "drivers/gpu/drm/msm",
        "drivers/gpu/drm",
    ]
    local_audio_paths = [
        "techpack/audio",
        "drivers/soundwire",
        "drivers/slimbus",
        "sound",
    ]
    local_thermal_paths = [
        "drivers/thermal",
        "drivers/power",
        "drivers/cpufreq",
    ]

    local_camera_signal = target_present and any(
        _path_exists(TARGET, p) for p in local_camera_paths
    )
    local_cam_isp_signal = target_present and (
        _path_exists(TARGET, "techpack/camera")
        or _path_exists(TARGET, "drivers/media/platform/msm/camera")
        or _path_exists(TARGET, "drivers/media/platform/qcom/camera")
    )
    local_display_signal = target_present and any(
        _path_exists(TARGET, p) for p in local_display_paths
    )
    local_audio_signal = target_present and any(
        _path_exists(TARGET, p) for p in local_audio_paths
    )
    local_thermal_signal = target_present and any(
        _path_exists(TARGET, p) for p in local_thermal_paths
    )

    cam_signal = local_camera_signal or _contains_any(
        copied_text, ["camera", "cam_sensor", "cam_isp", "camss"]
    )
    cam_isp_signal = local_cam_isp_signal or _contains_any(
        copied_text, ["cam_isp", "camss", "isp", "msm_isp"]
    )
    dsp_signal = local_display_signal or _contains_any(
        copied_text, ["display", "dsi", "drm", "msm_drm"]
    )
    thm_signal = local_thermal_signal or _contains_any(
        copied_text, ["thermal", "power", "qcom", "cpufreq"]
    )
    aud_signal = local_audio_signal or _contains_any(
        copied_text, ["audio", "snd", "wcd", "q6", "soundwire", "slimbus"]
    )
    xiaomi_signal = _contains_any(joined, ["xiaomi", "umi", "sm8250"])

    ref_camera_alignment = (
        "yes" if (bool(camera_ref_drivers) and xiaomi_signal) else "no"
    )
    ref_display_alignment = (
        "yes" if display_ref_repo == "utsavbalar1231/display-drivers" else "no"
    )
    ref_thermal_alignment = (
        "yes" if (("thermal" in so_ts_drivers) and xiaomi_signal) else "no"
    )
    ref_xiaomi_alignment = "yes" if xiaomi_signal else "no"

    partition_signal = _contains_any(
        rom_text, ["dynamic partition", "dynamic_partitions_op_list"]
    )

    lines = [
        "status=ok",
        f"boot_chain_match={boot_match}",
        f"dtbo_match={dtbo_match}",
        f"vbmeta_match={vbmeta_match}",
        f"partition_baseline_signal={'yes' if partition_signal else 'no'}",
        f"target_tree_present={'yes' if target_present else 'no'}",
        f"local_camera_signal={'yes' if local_camera_signal else 'no'}",
        f"local_camera_isp_signal={'yes' if local_cam_isp_signal else 'no'}",
        f"local_display_signal={'yes' if local_display_signal else 'no'}",
        f"local_audio_signal={'yes' if local_audio_signal else 'no'}",
        f"local_thermal_signal={'yes' if local_thermal_signal else 'no'}",
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
