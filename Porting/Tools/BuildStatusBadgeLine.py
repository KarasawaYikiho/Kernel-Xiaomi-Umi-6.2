#!/usr/bin/env python3
from pathlib import Path

from KvUtils import parse_kv
from Phase2Decision import derive_runtime_ready, driver_integration_allows_runtime

ART = Path("artifacts")
OUT = ART / "status-badge-line.txt"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    r = parse_kv(ART / "phase2-report.txt")

    build_rc = r.get("build_rc", "n/a")
    flash = r.get("flash_status", "unknown")
    anyk = r.get("anykernel_ok", "no")
    anyk_reason = r.get("anykernel_reason", "n/a")
    anyk_val = r.get("anykernel_validate_status", "unknown")
    ratio = r.get("manifest_hit_ratio", "0.000")
    next_action = r.get("next_action", "collect-more-data")
    runtime_ready = r.get("runtime_ready", "no")
    driver_integration = r.get("driver_integration_status", "pending")
    driver_pending = r.get("driver_integration_pending", "")
    runtime_result = r.get("runtime_validation_overall", "UNKNOWN")
    runtime_status = r.get("runtime_validation_status", "missing_input")
    runtime_boot_method = r.get("runtime_validation_boot_method", "unknown")
    failed_step = r.get("runtime_validation_failed_step", "")
    release_status = r.get("release_status", "unknown")
    rom_alignment = r.get("rom_alignment_status", "pending")
    rom_bootimg = f"{r.get('bootimg_rom_size_match', 'unknown')}/{r.get('bootimg_rom_header_version_match', 'unknown')}/{r.get('bootimg_official_reference_gate', 'no')}"
    magisk_ready = (
        "yes"
        if release_status == "ready"
        and r.get("bootimg_status", "missing") == "ok"
        and r.get("bootimg_rom_size_match", "unknown") == "yes"
        and r.get("bootimg_rom_header_version_match", "unknown") == "yes"
        and r.get("bootimg_official_reference_gate", "no") == "yes"
        else "no"
    )

    expected_runtime_ready = derive_runtime_ready(next_action)
    runtime_marker = (
        "ok"
        if runtime_ready == expected_runtime_ready
        else f"mismatch(expected:{expected_runtime_ready})"
    )
    runtime_gate = (
        "ready"
        if runtime_ready == "yes"
        and driver_integration_allows_runtime(driver_integration, driver_pending)
        else "blocked"
    )
    runtime_result_suffix = f"/{failed_step}" if failed_step else ""

    line = (
        f"build={build_rc} | flash={flash} | anykernel={anyk}/{anyk_reason}/{anyk_val} "
        f"| driver_integration={driver_integration} | rom_alignment={rom_alignment} | runtime_gate={runtime_gate} "
        f"| runtime_result={runtime_result}{runtime_result_suffix} "
        f"| runtime_status={runtime_status}/{runtime_boot_method} | magisk_ready={magisk_ready} "
        f"| runtime_ready={runtime_ready}({runtime_marker}) | release={release_status} "
        f"| rom_bootimg={rom_bootimg} | hit_ratio={ratio} | next={next_action}"
    )
    OUT.write_text(line + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
