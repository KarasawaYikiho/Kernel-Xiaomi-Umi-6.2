#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from KvUtils import parse_kv
from Manifest import normalize_item, parse_driver_manifest

ART = Path("artifacts")
MANIFEST = ART / "driver-integration-manifest.txt"
OUT = ART / "driver-integration-manifest-sync.txt"

REFERENCE_REPORT = Path("Porting/ReferenceDriversAnalysis.md")
ROM_REPORT = Path("Porting/OfficialRomAnalysis.md")
EVIDENCE = ART / "driver-integration-evidence.txt"

BASE_REQUIRED = [
    "display_pipeline",
    "audio_stack",
    "camera_sensor_module",
    "camera_isp_path",
    "thermal_power_tuning",
]

REF_REQUIRED = [
    "ref_driver_xiaomi_path_alignment",
    "ref_driver_camera_path_alignment",
    "ref_driver_display_path_alignment",
    "ref_driver_thermal_path_alignment",
]

ROM_REQUIRED = [
    "rom_dynamic_partition_baseline",
]

ROM_OPTIONAL_COMPARE = [
    "rom_boot_chain_consistency",
    "rom_dtbo_consistency",
    "rom_vbmeta_consistency",
]


def _has_text(path: Path, needle: str) -> bool:
    if not path.exists():
        return False
    return needle.lower() in path.read_text(encoding="utf-8", errors="ignore").lower()


def _detect_dynamic_partition_signal() -> bool:
    return (
        _has_text(ROM_REPORT, "dynamic partition")
        or _has_text(ROM_REPORT, "dynamic_partitions_op_list")
        or _has_text(ROM_REPORT, "dynamic partitions operation")
    )


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    comments, integrated, pending, unknown = parse_driver_manifest(MANIFEST)

    required = {normalize_item(x) for x in BASE_REQUIRED + REF_REQUIRED + ROM_REQUIRED}

    # If reports are missing, keep related tasks pending explicitly.
    reference_ready = REFERENCE_REPORT.exists()
    rom_ready = ROM_REPORT.exists()

    if not reference_ready:
        required.add("reference_driver_analysis_generation")
    if not rom_ready:
        required.add("official_rom_baseline_generation")

    # ROM evidence checks: if we have report but key signals are missing, keep explicit pending items.
    if rom_ready and not _detect_dynamic_partition_signal():
        required.add("rom_dynamic_partition_baseline")

    # Evidence-driven auto integration (conservative signals only).
    ev = parse_kv(EVIDENCE)
    evidence_promoted: list[str] = []

    compare_required: set[str] = set()
    if rom_ready:
        compare_required.update({normalize_item(x) for x in ROM_OPTIONAL_COMPARE})
    if ev.get("boot_local_path"):
        compare_required.add("rom_boot_chain_consistency")
    if ev.get("dtbo_local_path"):
        compare_required.add("rom_dtbo_consistency")
    if ev.get("vbmeta_local_path"):
        compare_required.add("rom_vbmeta_consistency")
    required.update(compare_required)

    if ev.get("camera_signal") == "yes":
        integrated.add("camera_sensor_module")
        evidence_promoted.append("camera_sensor_module")
    if ev.get("camera_isp_signal") == "yes":
        integrated.add("camera_isp_path")
        evidence_promoted.append("camera_isp_path")
    if ev.get("display_signal") == "yes":
        integrated.add("display_pipeline")
        evidence_promoted.append("display_pipeline")
    if ev.get("thermal_signal") == "yes":
        integrated.add("thermal_power_tuning")
        evidence_promoted.append("thermal_power_tuning")
    if ev.get("audio_signal") == "yes":
        integrated.add("audio_stack")
        evidence_promoted.append("audio_stack")

    if ev.get("ref_driver_xiaomi_alignment") == "yes":
        integrated.add("ref_driver_xiaomi_path_alignment")
        evidence_promoted.append("ref_driver_xiaomi_path_alignment")
    if ev.get("ref_driver_camera_alignment") == "yes":
        integrated.add("ref_driver_camera_path_alignment")
        evidence_promoted.append("ref_driver_camera_path_alignment")
    if ev.get("ref_driver_display_alignment") == "yes":
        integrated.add("ref_driver_display_path_alignment")
        evidence_promoted.append("ref_driver_display_path_alignment")
    if ev.get("ref_driver_thermal_alignment") == "yes":
        integrated.add("ref_driver_thermal_path_alignment")
        evidence_promoted.append("ref_driver_thermal_path_alignment")
    if ev.get("partition_baseline_signal") == "yes":
        integrated.add("rom_dynamic_partition_baseline")
        evidence_promoted.append("rom_dynamic_partition_baseline")
    if ev.get("boot_chain_match") == "yes":
        integrated.add("rom_boot_chain_consistency")
        evidence_promoted.append("rom_boot_chain_consistency")
    if ev.get("dtbo_match") == "yes":
        integrated.add("rom_dtbo_consistency")
        evidence_promoted.append("rom_dtbo_consistency")
    if ev.get("vbmeta_match") == "yes":
        integrated.add("rom_vbmeta_consistency")
        evidence_promoted.append("rom_vbmeta_consistency")

    # Ensure every required item is either integrated or pending.
    for item in required:
        if item not in integrated:
            pending.add(item)

    # integrated wins over pending when both exist; stale non-required pending items are dropped.
    pending = {x for x in pending if x not in integrated and x in required}

    out_lines: list[str] = []
    out_lines.append("# Driver integration manifest")
    out_lines.append("# Mark completed work with: integrated:<item>")
    out_lines.append("# Keep unfinished work as: pending:<item>")
    out_lines.append("# Auto-synced by Porting/Tools/SyncDriverIntegrationManifest.py")
    out_lines.append("")
    out_lines.append("# Core integration backlog")
    for item in sorted({normalize_item(x) for x in BASE_REQUIRED}):
        prefix = "integrated" if item in integrated else "pending"
        out_lines.append(f"{prefix}:{item}")

    out_lines.append("")
    out_lines.append("# Reference driver alignment backlog")
    for item in sorted({normalize_item(x) for x in REF_REQUIRED}):
        prefix = "integrated" if item in integrated else "pending"
        out_lines.append(f"{prefix}:{item}")

    out_lines.append("")
    out_lines.append("# Official ROM validation backlog")
    for item in sorted({normalize_item(x) for x in ROM_REQUIRED} | compare_required):
        prefix = "integrated" if item in integrated else "pending"
        out_lines.append(f"{prefix}:{item}")

    extra_items = sorted(integrated - required)
    if extra_items:
        out_lines.append("")
        out_lines.append("# Extra custom items")
        for item in extra_items:
            prefix = "integrated" if item in integrated else "pending"
            out_lines.append(f"{prefix}:{item}")

    if unknown:
        out_lines.append("")
        out_lines.append("# Unknown legacy lines preserved for manual review")
        for raw in sorted(unknown):
            out_lines.append(f"# legacy:{raw}")

    MANIFEST.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    sync_lines = [
        f"status=ok",
        f"reference_report_ready={'yes' if reference_ready else 'no'}",
        f"rom_report_ready={'yes' if rom_ready else 'no'}",
        f"evidence_file_present={'yes' if EVIDENCE.exists() else 'no'}",
        f"evidence_promoted={','.join(sorted(set(evidence_promoted)))}",
        f"integrated_count={len(integrated)}",
        f"pending_count={len(pending)}",
        f"unknown_legacy_lines={len(unknown)}",
    ]
    OUT.write_text("\n".join(sync_lines) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
