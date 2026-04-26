#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from KvUtils import parse_kv
from Manifest import normalize_item, parse_driver_manifest

ART = Path("artifacts")
MANIFEST = ART / "rom-alignment-manifest.txt"
OUT = ART / "rom-alignment-manifest-sync.txt"

ROM_REPORT = Path("Porting/OfficialRomAnalysis.md")

REQUIRED = [
    "bootimg_release_packaging",
    "rom_boot_chain_consistency",
    "rom_dtbo_consistency",
    "rom_vbmeta_consistency",
    "rom_dynamic_partition_baseline",
    "dtb_target_coverage",
    "runtime_validation_official_rom",
]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    _, integrated, pending, unknown = parse_driver_manifest(MANIFEST)
    required = {normalize_item(item) for item in REQUIRED}

    boot = parse_kv(ART / "bootimg-info.txt")
    evidence = parse_kv(ART / "driver-integration-evidence.txt")
    dtb = parse_kv(ART / "dtb-postcheck.txt")
    runtime_result = parse_kv(ART / "runtime-validation-result.txt")

    evidence_promoted: list[str] = []

    if boot.get("status") == "ok" and boot.get("flash_ready") == "yes":
        integrated.add("bootimg_release_packaging")
        evidence_promoted.append("bootimg_release_packaging")

    if evidence.get("boot_chain_match") == "yes":
        integrated.add("rom_boot_chain_consistency")
        evidence_promoted.append("rom_boot_chain_consistency")
    if evidence.get("dtbo_match") == "yes":
        integrated.add("rom_dtbo_consistency")
        evidence_promoted.append("rom_dtbo_consistency")
    if evidence.get("vbmeta_match") == "yes":
        integrated.add("rom_vbmeta_consistency")
        evidence_promoted.append("rom_vbmeta_consistency")
    if evidence.get("partition_baseline_signal") == "yes" and ROM_REPORT.exists():
        integrated.add("rom_dynamic_partition_baseline")
        evidence_promoted.append("rom_dynamic_partition_baseline")
    if dtb.get("miss", "0") == "0" and dtb.get("wanted", "0") != "0":
        integrated.add("dtb_target_coverage")
        evidence_promoted.append("dtb_target_coverage")

    runtime_overall = runtime_result.get("overall", "UNKNOWN")
    if runtime_overall == "PASS":
        integrated.add("runtime_validation_official_rom")
        evidence_promoted.append("runtime_validation_official_rom")

    for item in required:
        if item not in integrated:
            pending.add(item)

    pending = {item for item in pending if item in required and item not in integrated}

    lines = [
        "# ROM alignment manifest",
        "# Mark completed work with: integrated:<item>",
        "# Keep unfinished work as: pending:<item>",
        "# Auto-synced by Porting/Tools/SyncRomAlignmentManifest.py",
        "",
        "# Release-chain alignment backlog",
    ]
    for item in sorted(required):
        prefix = "integrated" if item in integrated else "pending"
        lines.append(f"{prefix}:{item}")

    if unknown:
        lines.extend(
            [
                "",
                "# Unknown legacy lines preserved for manual review",
                *[f"# legacy:{raw}" for raw in sorted(unknown)],
            ]
        )

    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT.write_text(
        "\n".join(
            [
                "status=ok",
                f"rom_report_ready={'yes' if ROM_REPORT.exists() else 'no'}",
                f"integrated_count={len(integrated)}",
                f"pending_count={len(pending)}",
                f"evidence_promoted={','.join(sorted(set(evidence_promoted)))}",
                f"unknown_legacy_lines={len(unknown)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {MANIFEST}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
