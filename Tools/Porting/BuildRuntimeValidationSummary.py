#!/usr/bin/env python3
from pathlib import Path

from KvUtils import parse_kv, split_csv
from Phase2Decision import driver_integration_runtime_blockers

ART = Path("artifacts")
OUT = ART / "runtime-validation-summary.md"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    report = parse_kv(ART / "phase2-report.txt")
    consistency = parse_kv(ART / "decision-consistency.txt")
    focus = parse_kv(ART / "next-focus.txt")
    meta = parse_kv(ART / "run-meta.txt")
    runtime_result = parse_kv(ART / "runtime-validation-result.txt")

    next_action = report.get("next_action", "collect-more-data")
    runtime_ready = report.get("runtime_ready", "no")
    consistency_status = consistency.get("status", "unknown")
    consistency_errors = consistency.get("errors", "")
    driver_status = report.get("driver_integration_status", "pending")
    driver_pending = report.get("driver_integration_pending", "")
    driver_runtime_blockers = driver_integration_runtime_blockers(
        driver_status, driver_pending
    )
    bootimg_status = report.get("bootimg_status", "missing")
    bootimg_build_status = report.get("bootimg_build_status", "unknown")
    bootimg_build_missing = report.get("bootimg_build_missing", "")
    release_status = report.get("release_status", "unknown")
    anykernel_ok = report.get("anykernel_ok", "no")
    phase2_complete = report.get("phase2_complete", "no")
    phase2_blockers = split_csv(report.get("phase2_blockers", ""))

    runtime_blockers: list[str] = []
    phase2_runtime_blockers: list[str] = []
    if report.get("defconfig_rc", "n/a") not in ("0", "n/a"):
        phase2_runtime_blockers.append(f"defconfig_rc={report.get('defconfig_rc', 'n/a')}")
    if report.get("build_rc", "n/a") not in ("0", "n/a"):
        phase2_runtime_blockers.append(f"build_rc={report.get('build_rc', 'n/a')}")
    if report.get("dtbs_rc", "n/a") not in ("0", "n/a"):
        phase2_runtime_blockers.append(f"dtbs_rc={report.get('dtbs_rc', 'n/a')}")
    if report.get("flash_status", "unknown") != "candidate":
        phase2_runtime_blockers.append(f"flash_status={report.get('flash_status', 'unknown')}")
    if phase2_complete != "yes" and not phase2_blockers and not phase2_runtime_blockers:
        phase2_runtime_blockers.append("phase2_complete!=yes")
    for blocker in phase2_blockers:
        if blocker not in phase2_runtime_blockers:
            phase2_runtime_blockers.append(blocker)
    runtime_blockers.extend(phase2_runtime_blockers)
    phase3_blockers = [f"driver_integration_pending={x}" for x in driver_runtime_blockers]
    runtime_blockers.extend(phase3_blockers)
    if consistency_status not in ("ok", "unknown"):
        runtime_blockers.append(f"decision_consistency={consistency_status}")
    if consistency_errors:
        runtime_blockers.append(f"decision_consistency_errors={consistency_errors}")
    release_followups: list[str] = []
    if bootimg_status != "ok":
        release_followups.append(f"bootimg_status={bootimg_status}")
    if bootimg_build_status not in ("ok", "unknown"):
        release_followups.append(f"bootimg_build_status={bootimg_build_status}")
    if bootimg_build_missing:
        release_followups.extend(
            [f"bootimg_build_missing={x}" for x in split_csv(bootimg_build_missing)]
        )
    if driver_pending:
        release_followups.extend(
            [
                f"driver_followup={x}"
                for x in split_csv(driver_pending)
                if x not in driver_runtime_blockers
            ]
        )

    magisk_patch_ready = (
        release_status == "ready"
        and bootimg_status == "ok"
        and report.get("bootimg_rom_size_match", "unknown") == "yes"
        and report.get("bootimg_rom_header_version_match", "unknown") == "yes"
        and report.get("bootimg_official_reference_gate", "no") == "yes"
    )

    if not magisk_patch_ready:
        if report.get("anykernel_ok", "no") != "yes":
            runtime_blockers.append("anykernel_ok!=yes")
        if report.get("anykernel_validate_status", "unknown") not in ("ok", "unknown"):
            runtime_blockers.append(
                f"anykernel_validate_status={report.get('anykernel_validate_status', 'unknown')}"
            )
        if runtime_ready != "yes":
            runtime_blockers.append(f"runtime_ready={runtime_ready}")
    else:
        runtime_blockers = [
            x for x in runtime_blockers if not x.startswith("flash_status=")
        ]

    headline = (
        "READY FOR MAGISK-PATCHED BOOT VALIDATION"
        if not runtime_blockers
        else "NOT READY FOR DEVICE RUNTIME VALIDATION"
    )

    md = [
        "# Runtime Validation Summary",
        "",
        f"**Status:** `{headline}`",
        "",
        "## Snapshot",
        f"- Device: `{report.get('device', meta.get('device', 'unknown'))}`",
        f"- Run: `{meta.get('run_number', '?')}`",
        f"- SHA: `{meta.get('sha', '')}`",
        f"- next_action: `{next_action}`",
        f"- phase2_complete: `{phase2_complete}`",
        f"- runtime_ready: `{runtime_ready}`",
        f"- decision_consistency: `{consistency_status}`",
        f"- driver_integration_status: `{driver_status}`",
        f"- flash_status: `{report.get('flash_status', 'unknown')}`",
        f"- anykernel: `{report.get('anykernel_ok', 'no')}/{report.get('anykernel_validate_status', 'unknown')}`",
        f"- magisk_patch_ready: `{'yes' if magisk_patch_ready else 'no'}`",
        f"- focus: `{focus.get('focus', '')}` ({focus.get('reason', 'n/a')})",
        f"- result_overall: `{runtime_result.get('overall', 'UNKNOWN')}`",
        f"- boot_method: `{runtime_result.get('boot_method', 'unknown')}`",
        f"- patched_boot_image: `{runtime_result.get('patched_boot_image', '') or 'not_recorded'}`",
        f"- result_failed_step: `{runtime_result.get('failed_step', '') or 'none'}`",
        "",
    ]

    if runtime_blockers:
        md.extend(
            [
                "## Phase 2 Blockers",
                *(
                    [f"- {x}" for x in phase2_runtime_blockers]
                    if phase2_runtime_blockers
                    else ["- none"]
                ),
                "",
                "## Phase 3 Usability Blockers",
                *([f"- {x}" for x in phase3_blockers] if phase3_blockers else ["- none"]),
                "",
                "## Phase 4 Runtime Validation",
                "- blocked until Phase 2 and Phase 3 exit criteria are complete",
                "",
            ]
        )
    else:
        md.extend(
            [
                "## Runtime Gate Result",
                "- ROM-aligned boot packaging is ready for device-side Magisk patch validation.",
                "- Driver integration has no remaining runtime-blocking items.",
                "- AnyKernel packaging is no longer the primary gate for the current validation path.",
                "",
            ]
        )

    if release_followups:
        md.extend(
            [
                "## Release / Alignment Follow-ups",
                *[f"- {x}" for x in release_followups],
                "",
            ]
        )

    next_steps = [
        "- Copy `artifacts/boot.img` to the device and patch it with the Magisk app.",
        "- Flash the Magisk-patched boot image, then confirm the device still boots cleanly.",
        "- After the first rooted boot, collect dmesg/logcat and rerun postprocess with the validation result.",
    ]
    runtime_overall = runtime_result.get("overall", "UNKNOWN")
    runtime_status = runtime_result.get("status", "missing_input")
    if runtime_overall == "FAIL":
        next_steps = [
            "- Inspect `runtime-validation-result.txt` and `phase2-report.txt` for the failing step.",
            "- Attach dmesg/logcat plus the exact failed checklist item for the next patch round.",
            "- Keep the known-good rollback path ready before the next test build.",
        ]
    elif runtime_overall == "PASS":
        next_steps = [
            "- Runtime validation passed; switch focus from device smoke test to release hardening.",
            "- If `bootimg_status` is not `ok`, continue with release `boot.img` preparation.",
            "- If release packaging is already green, close remaining ROM / driver alignment follow-ups.",
        ]
    elif runtime_blockers:
        if magisk_patch_ready:
            next_steps = [
                "- Release boot image is already ready; keep the Magisk-patched boot path as the target validation route.",
                "- Clear the listed runtime blockers before asking for another device-side validation pass.",
                "- Treat AnyKernel packaging as secondary evidence rather than the primary path.",
                "- After the blockers are cleared, rerun postprocess and continue with the Magisk-patched boot flow.",
            ]
        else:
            next_steps = [
                "- Finish release boot image preparation before device-side validation.",
                "- Clear the listed runtime blockers before asking for another device-side validation pass.",
                "- If AnyKernel packaging is available earlier, treat it as secondary evidence rather than the primary path.",
                "- After packaging is ready, rerun postprocess and continue with the Magisk-patched boot flow.",
            ]
    elif runtime_status == "awaiting_device_validation":
        next_steps = [
            "- Patch `artifacts/boot.img` with Magisk and note the patched image filename in `meta.patched_boot_image`.",
            "- Flash the patched boot image, complete the checklist items, then change the `check.*` lines from `UNKNOWN`.",
            "- After the first device run, attach dmesg/logcat references in the same input file and rerun postprocess.",
        ]

    md.extend(
        [
            "## First Files To Open",
            "- `runtime-validation-summary.md`",
            "- `phase2-report.txt`",
            "- `status-badge-line.txt`",
            "- `action-validation-checklist.md`",
            "- `artifact-summary.md`",
            "",
            "## Device-Side Next Step",
            *next_steps,
            "",
        ]
    )

    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
