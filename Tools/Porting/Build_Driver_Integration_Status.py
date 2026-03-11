#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ART = Path("artifacts")
OUT = ART / "driver-integration-status.txt"


def _has_text(path: Path, needle: str) -> bool:
    if not path.exists():
        return False
    return needle.lower() in path.read_text(encoding="utf-8", errors="ignore").lower()


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    reference_report = Path("Porting/Reference-Drivers-Analysis.md")
    rom_report = Path("Porting/OfficialRom-Umi-Os1.0.5.0-Analysis.md")
    manifest = ART / "driver-integration-manifest.txt"

    reference_ready = reference_report.exists()
    rom_ready = rom_report.exists()
    has_camera_focus = _has_text(reference_report, "cam_sensor_module")
    has_partition_baseline = _has_text(rom_report, "dynamic partition") or _has_text(rom_report, "dynamic partitions")

    integrated_count = 0
    pending = []

    if manifest.exists():
        for raw in manifest.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("integrated:"):
                integrated_count += 1
            elif line.startswith("pending:"):
                pending.append(line.split(":", 1)[1].strip())

    if not reference_ready:
        pending.append("missing_reference_driver_analysis")
    if not rom_ready:
        pending.append("missing_official_rom_baseline")
    if reference_ready and not has_camera_focus:
        pending.append("camera_focus_not_confirmed")
    if rom_ready and not has_partition_baseline:
        pending.append("partition_baseline_not_confirmed")

    if integrated_count >= 3 and not pending:
        status = "complete"
        reason = "integration_manifest_complete"
    elif integrated_count > 0:
        status = "partial"
        reason = "integration_manifest_partial"
    else:
        status = "pending"
        reason = "integration_manifest_missing_or_empty"

    OUT.write_text(
        "\n".join([
            f"status={status}",
            f"reason={reason}",
            f"integrated_count={integrated_count}",
            f"reference_report_ready={'yes' if reference_ready else 'no'}",
            f"rom_baseline_ready={'yes' if rom_ready else 'no'}",
            f"camera_focus_ready={'yes' if has_camera_focus else 'no'}",
            f"partition_baseline_ready={'yes' if has_partition_baseline else 'no'}",
            "pending=" + ",".join(dict.fromkeys(pending)),
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
