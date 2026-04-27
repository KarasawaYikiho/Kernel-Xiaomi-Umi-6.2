#!/usr/bin/env python3
from pathlib import Path
import json

from KvUtils import parse_kv
from Phase2Decision import (
    DEFAULT_BOOTIMG_REQUIRED_BYTES_STR,
    driver_integration_allows_runtime,
)

ART = Path("artifacts")
OUT = ART / "phase2-metrics.json"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    report = parse_kv(ART / "phase2-report.txt")
    meta = parse_kv(ART / "run-meta.txt")
    valid = parse_kv(ART / "phase2-report-validate.txt")
    consistency = parse_kv(ART / "decision-consistency.txt")
    runtime_result = parse_kv(ART / "runtime-validation-result.txt")

    runtime_gate_status = (
        "ready"
        if report.get("runtime_ready", "no") == "yes"
        and consistency.get("status", "unknown") in ("ok", "unknown")
        and driver_integration_allows_runtime(
            report.get("driver_integration_status", "pending"),
            report.get("driver_integration_pending", ""),
        )
        else "blocked"
    )
    fastboot_boot_package_ready = (
        report.get("release_status", "unknown") == "ready"
        and report.get("bootimg_status", "missing") == "ok"
        and report.get("bootimg_rom_size_match", "unknown") == "yes"
        and report.get("bootimg_rom_header_version_match", "unknown") == "yes"
        and report.get("bootimg_official_reference_gate", "no") == "yes"
    )

    obj = {
        "run": {
            "id": meta.get("run_id", ""),
            "number": meta.get("run_number", ""),
            "sha": meta.get("sha", ""),
            "device": meta.get("device", report.get("device", "unknown")),
        },
        "build": {
            "defconfig_rc": report.get("defconfig_rc", "n/a"),
            "build_rc": report.get("build_rc", "n/a"),
        },
        "dtb": {
            "hit_ratio": report.get("manifest_hit_ratio", "0.000"),
            "miss_bucket_total": report.get("miss_bucket_total", "0"),
            "manifest_wanted": report.get("manifest_wanted", "0"),
            "manifest_hit": report.get("manifest_hit", "0"),
            "manifest_miss": report.get("manifest_miss", "0"),
        },
        "packaging": {
            "flash_status": report.get("flash_status", "unknown"),
            "release_status": report.get("release_status", "unknown"),
            "release_reason": report.get("release_reason", "n/a"),
            "anykernel_ok": report.get("anykernel_ok", "no"),
            "anykernel_reason": report.get("anykernel_reason", "n/a"),
            "anykernel_imagegz_path": report.get("anykernel_imagegz_path", ""),
            "anykernel_template_source": report.get("anykernel_template_source", ""),
            "anykernel_validate_status": report.get(
                "anykernel_validate_status", "unknown"
            ),
            "anykernel_validate_reason": report.get("anykernel_validate_reason", "n/a"),
            "bootimg_status": report.get("bootimg_status", "missing"),
            "bootimg_reason": report.get("bootimg_reason", "n/a"),
            "bootimg_size_bytes": report.get("bootimg_size_bytes", "0"),
            "bootimg_required_bytes": report.get(
                "bootimg_required_bytes", DEFAULT_BOOTIMG_REQUIRED_BYTES_STR
            ),
            "bootimg_required_bytes_parse": report.get(
                "bootimg_required_bytes_parse", "unknown"
            ),
            "bootimg_rom_expected_size_bytes": report.get(
                "bootimg_rom_expected_size_bytes", ""
            ),
            "bootimg_rom_expected_sha256": report.get(
                "bootimg_rom_expected_sha256", ""
            ),
            "bootimg_rom_expected_header_version": report.get(
                "bootimg_rom_expected_header_version", ""
            ),
            "bootimg_rom_size_match": report.get("bootimg_rom_size_match", "unknown"),
            "bootimg_rom_sha256_match": report.get(
                "bootimg_rom_sha256_match", "unknown"
            ),
            "bootimg_rom_header_version_match": report.get(
                "bootimg_rom_header_version_match", "unknown"
            ),
            "bootimg_official_reference_present": report.get(
                "bootimg_official_reference_present", "no"
            ),
            "bootimg_official_reference_gate": report.get(
                "bootimg_official_reference_gate", "no"
            ),
            "bootimg_official_reference_gate_reasons": report.get(
                "bootimg_official_reference_gate_reasons", ""
            ),
            "bootimg_build_source": report.get("bootimg_build_source", ""),
            "bootimg_build_source_ref": report.get("bootimg_build_source_ref", ""),
            "bootimg_build_status": report.get("bootimg_build_status", "unknown"),
            "bootimg_build_reason": report.get("bootimg_build_reason", "n/a"),
            "bootimg_build_missing": report.get("bootimg_build_missing", ""),
        },
        "report": {
            "next_action": report.get("next_action", "collect-more-data"),
            "runtime_ready": report.get("runtime_ready", "no"),
            "runtime_gate_status": runtime_gate_status,
            "fastboot_boot_package_ready": "yes" if fastboot_boot_package_ready else "no",
            "driver_integration_status": report.get(
                "driver_integration_status", "pending"
            ),
            "driver_integration_reason": report.get("driver_integration_reason", "n/a"),
            "schema_status": valid.get("status", "unknown"),
        },
        "consistency": {
            "status": consistency.get("status", "unknown"),
            "errors": consistency.get("errors", ""),
            "expected_runtime_ready": consistency.get("expected_runtime_ready", ""),
            "expected_focus": consistency.get("expected_focus", ""),
        },
        "runtime_validation": {
            "status": runtime_result.get("status", "missing_input"),
            "overall": runtime_result.get("overall", "UNKNOWN"),
            "boot_method": runtime_result.get("boot_method", "unknown"),
            "patched_boot_image": runtime_result.get("patched_boot_image", ""),
            "failed_step": runtime_result.get("failed_step", ""),
            "pass_count": runtime_result.get("pass_count", "0"),
            "fail_count": runtime_result.get("fail_count", "0"),
            "skip_count": runtime_result.get("skip_count", "0"),
            "unknown_count": runtime_result.get("unknown_count", "0"),
        },
    }

    OUT.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
