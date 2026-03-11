#!/usr/bin/env python3
from pathlib import Path

from Kv_Utils import parse_kv
from Phase2_Decision import DEFAULT_BOOTIMG_REQUIRED_BYTES_STR

ART = Path("artifacts")
OUT = ART / "action-validation-checklist.md"



def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    report = parse_kv(ART / "phase2-report.txt")
    meta = parse_kv(ART / "run-meta.txt")
    consistency = parse_kv(ART / "decision-consistency.txt")

    device = report.get("device", meta.get("device", "umi"))
    run_no = meta.get("run_number", "?")
    sha = meta.get("sha", "")
    next_action = report.get("next_action", "collect-more-data")
    runtime_ready = report.get("runtime_ready", "no")
    bootimg_status = report.get("bootimg_status", "missing")
    bootimg_build_status = report.get("bootimg_build_status", "unknown")
    bootimg_build_missing = report.get("bootimg_build_missing", "")
    bootimg_size = report.get("bootimg_size_bytes", "0")
    bootimg_required = report.get("bootimg_required_bytes", DEFAULT_BOOTIMG_REQUIRED_BYTES_STR)
    bootimg_required_parse = report.get("bootimg_required_bytes_parse", "unknown")
    consistency_status = consistency.get("status", "unknown")
    consistency_errors = consistency.get("errors", "")
    driver_integration_status = report.get("driver_integration_status", "pending")
    driver_integration_reason = report.get("driver_integration_reason", "n/a")
    blockers = []
    if report.get("defconfig_rc", "n/a") not in ("0", "n/a"):
        blockers.append(f"defconfig_rc={report.get('defconfig_rc', 'n/a')}")
    if report.get("build_rc", "n/a") not in ("0", "n/a"):
        blockers.append(f"build_rc={report.get('build_rc', 'n/a')}")
    if report.get("dtbs_rc", "n/a") not in ("0", "n/a"):
        blockers.append(f"dtbs_rc={report.get('dtbs_rc', 'n/a')}")
    if report.get("anykernel_ok", "no") != "yes":
        blockers.append("anykernel_ok!=yes")
    if report.get("anykernel_validate_status", "unknown") not in ("ok", "unknown"):
        blockers.append(f"anykernel_validate_status={report.get('anykernel_validate_status', 'unknown')}")
    if bootimg_status != "ok":
        blockers.append(f"bootimg_status={bootimg_status}")
    if bootimg_build_status not in ("ok", "unknown"):
        blockers.append(f"bootimg_build_status={bootimg_build_status}")
    if bootimg_build_missing:
        blockers.append(f"bootimg_build_missing={bootimg_build_missing}")
    if consistency_status not in ("ok", "unknown"):
        blockers.append(f"decision_consistency={consistency_status}")
    if consistency_errors:
        blockers.append(f"decision_consistency_errors={consistency_errors}")
    if driver_integration_status != "complete":
        blockers.append(f"driver_integration_status={driver_integration_status}")

    md = [
        "# Phase2 Runtime Validation Checklist",
        "",
        f"- Device: `{device}`",
        f"- Run: `{run_no}`",
        f"- SHA: `{sha}`",
        f"- next_action: `{next_action}`",
        f"- runtime_ready: `{runtime_ready}`",
        f"- bootimg_status: `{bootimg_status}`",
        f"- bootimg_build_status: `{bootimg_build_status}`",
        f"- bootimg_size_bytes: `{bootimg_size}`",
        f"- bootimg_required_bytes: `{bootimg_required}`",
        f"- bootimg_required_bytes_parse: `{bootimg_required_parse}`",
        f"- decision_consistency: `{consistency_status}`",
        f"- decision_consistency_errors: `{consistency_errors or 'none'}`",
        f"- driver_integration_status: `{driver_integration_status}`",
        f"- driver_integration_reason: `{driver_integration_reason}`",
        "",
        "## Decision",
        "- [ ] If `runtime_ready=yes`, `decision_consistency=ok`, and `driver_integration_status=complete`, proceed with device runtime validation.",
        "- [ ] If any of the above is not satisfied, stop and finish driver integration / report blockers first.",
        "",
    ]

    if blockers:
        md.extend([
            "## Blockers (from phase2-report)",
            *[f"- {b}" for b in blockers],
            "",
        ])

    md.extend([
        "## Pre-check",
        "- [ ] Confirm battery >= 50% and USB debugging available.",
        "- [ ] Confirm bootloader/unlock state and recovery path prepared.",
        "- [ ] Keep previous known-good boot image for rollback.",
        "",
        "## Flash & Boot",
        "- [ ] Flash `AnyKernel3-umi-candidate.zip` in recovery/fastboot flow.",
        "- [ ] First boot completes without bootloop (wait 3-5 min).",
        "- [ ] `adb shell uname -a` returns expected kernel build.",
        "",
        "## Smoke Tests",
        "- [ ] Wi-Fi/BT/mobile network basic connectivity.",
        "- [ ] Touchscreen/audio/camera basic functionality.",
        "- [ ] Charging + thermal behavior appears normal.",
        "",
        "## Stability",
        "- [ ] 15-30 min idle: no panic/reboot.",
        "- [ ] 10-15 min light load: no abnormal throttling/reboot.",
        "",
        "## Report Back",
        "- [ ] Export dmesg/logcat snippets if anomaly appears.",
        "- [ ] Provide pass/fail + failing step index for next patch round.",
        "",
    ])

    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
