#!/usr/bin/env python3
from pathlib import Path
import json

from Kv_Utils import parse_kv
from Phase2_Decision import DEFAULT_BOOTIMG_REQUIRED_BYTES_STR

ART = Path("artifacts")
OUT = ART / "phase2-metrics.json"



def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    report = parse_kv(ART / "phase2-report.txt")
    meta = parse_kv(ART / "run-meta.txt")
    valid = parse_kv(ART / "phase2-report-validate.txt")
    consistency = parse_kv(ART / "decision-consistency.txt")

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
        },
        "packaging": {
            "flash_status": report.get("flash_status", "unknown"),
            "anykernel_ok": report.get("anykernel_ok", "no"),
            "anykernel_validate_status": report.get("anykernel_validate_status", "unknown"),
            "anykernel_validate_reason": report.get("anykernel_validate_reason", "n/a"),
            "bootimg_status": report.get("bootimg_status", "missing"),
            "bootimg_reason": report.get("bootimg_reason", "n/a"),
            "bootimg_size_bytes": report.get("bootimg_size_bytes", "0"),
            "bootimg_required_bytes": report.get("bootimg_required_bytes", DEFAULT_BOOTIMG_REQUIRED_BYTES_STR),
            "bootimg_required_bytes_parse": report.get("bootimg_required_bytes_parse", "unknown"),
            "bootimg_build_status": report.get("bootimg_build_status", "unknown"),
            "bootimg_build_reason": report.get("bootimg_build_reason", "n/a"),
            "bootimg_build_missing": report.get("bootimg_build_missing", ""),
        },
        "report": {
            "next_action": report.get("next_action", "collect-more-data"),
            "runtime_ready": report.get("runtime_ready", "no"),
            "driver_integration_status": report.get("driver_integration_status", "pending"),
            "driver_integration_reason": report.get("driver_integration_reason", "n/a"),
            "schema_status": valid.get("status", "unknown"),
        },
        "consistency": {
            "status": consistency.get("status", "unknown"),
            "errors": consistency.get("errors", ""),
            "expected_runtime_ready": consistency.get("expected_runtime_ready", ""),
            "expected_focus": consistency.get("expected_focus", ""),
        },
    }

    OUT.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
