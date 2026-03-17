#!/usr/bin/env python3
from pathlib import Path

from Kv_Utils import parse_kv

ART = Path("artifacts")
OUT = ART / "runtime-validation-summary.md"


def _split_csv(value: str) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


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
    bootimg_status = report.get("bootimg_status", "missing")
    bootimg_build_status = report.get("bootimg_build_status", "unknown")
    bootimg_build_missing = report.get("bootimg_build_missing", "")

    runtime_blockers: list[str] = []
    if report.get("defconfig_rc", "n/a") not in ("0", "n/a"):
        runtime_blockers.append(f"defconfig_rc={report.get('defconfig_rc', 'n/a')}")
    if report.get("build_rc", "n/a") not in ("0", "n/a"):
        runtime_blockers.append(f"build_rc={report.get('build_rc', 'n/a')}")
    if report.get("dtbs_rc", "n/a") not in ("0", "n/a"):
        runtime_blockers.append(f"dtbs_rc={report.get('dtbs_rc', 'n/a')}")
    if report.get("flash_status", "unknown") != "candidate":
        runtime_blockers.append(f"flash_status={report.get('flash_status', 'unknown')}")
    if report.get("anykernel_ok", "no") != "yes":
        runtime_blockers.append("anykernel_ok!=yes")
    if report.get("anykernel_validate_status", "unknown") not in ("ok", "unknown"):
        runtime_blockers.append(f"anykernel_validate_status={report.get('anykernel_validate_status', 'unknown')}")
    if driver_status != "complete":
        runtime_blockers.append(f"driver_integration_status={driver_status}")
    if consistency_status not in ("ok", "unknown"):
        runtime_blockers.append(f"decision_consistency={consistency_status}")
    if consistency_errors:
        runtime_blockers.append(f"decision_consistency_errors={consistency_errors}")
    if runtime_ready != "yes":
        runtime_blockers.append(f"runtime_ready={runtime_ready}")

    release_followups: list[str] = []
    if bootimg_status != "ok":
        release_followups.append(f"bootimg_status={bootimg_status}")
    if bootimg_build_status not in ("ok", "unknown"):
        release_followups.append(f"bootimg_build_status={bootimg_build_status}")
    if bootimg_build_missing:
        release_followups.extend([f"bootimg_build_missing={x}" for x in _split_csv(bootimg_build_missing)])

    headline = "READY FOR DEVICE RUNTIME VALIDATION" if not runtime_blockers else "NOT READY FOR DEVICE RUNTIME VALIDATION"

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
        f"- runtime_ready: `{runtime_ready}`",
        f"- decision_consistency: `{consistency_status}`",
        f"- driver_integration_status: `{driver_status}`",
        f"- flash_status: `{report.get('flash_status', 'unknown')}`",
        f"- anykernel: `{report.get('anykernel_ok', 'no')}/{report.get('anykernel_validate_status', 'unknown')}`",
        f"- focus: `{focus.get('focus', '')}` ({focus.get('reason', 'n/a')})",
        f"- result_overall: `{runtime_result.get('overall', 'UNKNOWN')}`",
        f"- result_failed_step: `{runtime_result.get('failed_step', '') or 'none'}`",
        "",
    ]

    if runtime_blockers:
        md.extend([
            "## Runtime Blockers",
            *[f"- {x}" for x in runtime_blockers],
            "",
        ])
    else:
        md.extend([
            "## Runtime Gate Result",
            "- Candidate packaging is ready for device-side runtime validation.",
            "- Driver integration gate is complete.",
            "- Remaining release bootimg work is tracked separately and does not block AnyKernel-based runtime testing.",
            "",
        ])

    if release_followups:
        md.extend([
            "## Release Bootimg Follow-ups",
            *[f"- {x}" for x in release_followups],
            "",
        ])

    md.extend([
        "## First Files To Open",
        "- `runtime-validation-summary.md`",
        "- `phase2-report.txt`",
        "- `status-badge-line.txt`",
        "- `action-validation-checklist.md`",
        "- `artifact-summary.md`",
        "",
        "## Device-Side Next Step",
        "- Flash `AnyKernel3-umi-candidate.zip` using the prepared validation flow.",
        "- Fill `runtime-validation-input.md` after testing, then run postprocess again.",
        "- If something fails, capture dmesg/logcat and the failing checklist step index.",
        "",
    ])

    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
