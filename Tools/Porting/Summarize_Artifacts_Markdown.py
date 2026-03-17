#!/usr/bin/env python3
from pathlib import Path

from Kv_Utils import parse_kv

ART = Path("artifacts")
OUT = ART / "artifact-summary.md"



def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    r = parse_kv(ART / "phase2-report.txt")
    n = parse_kv(ART / "next-focus.txt")
    c = parse_kv(ART / "artifact-completeness.txt")
    d = parse_kv(ART / "decision-consistency.txt")
    rv = parse_kv(ART / "runtime-validation-result.txt")

    next_action = r.get('next_action', '')

    runtime_gate = "ready" if r.get('runtime_ready', 'no') == 'yes' and r.get('driver_integration_status', 'pending') == 'complete' and d.get('status', 'unknown') in ('ok', 'unknown') else 'blocked'

    md = [
        "# Phase2 Artifact Summary",
        "",
        f"- Device: `{r.get('device', 'unknown')}`",
        f"- Build RC: `{r.get('build_rc', 'n/a')}` (defconfig `{r.get('defconfig_rc', 'n/a')}`)",
        f"- Flash Status: `{r.get('flash_status', 'unknown')}`",
        f"- AnyKernel OK: `{r.get('anykernel_ok', 'no')}`",
        f"- AnyKernel Validate: `{r.get('anykernel_validate_status', 'unknown')}` ({r.get('anykernel_validate_reason', 'n/a')})",
        f"- Manifest Hit Ratio: `{r.get('manifest_hit_ratio', '0.000')}`",
        f"- Artifact Completeness: `{c.get('status', 'unknown')}`",
        f"- Runtime Gate: `{runtime_gate}`",
        f"- Runtime Ready: `{r.get('runtime_ready', 'no')}`",
        f"- Driver Integration: `{r.get('driver_integration_status', 'pending')}` ({r.get('driver_integration_reason', 'n/a')})",
        f"- Decision Consistency: `{d.get('status', 'unknown')}`",
        f"- Runtime Validation Result: `{rv.get('overall', 'UNKNOWN')}` ({rv.get('status', 'missing_input')})",
        f"- Runtime Validation Failed Step: `{rv.get('failed_step', '') or 'none'}`",
        f"- Boot Image: `{r.get('bootimg_status', 'missing')}` ({r.get('bootimg_reason', 'n/a')}) - release follow-up",
        f"- Boot Image Build: `{r.get('bootimg_build_status', 'unknown')}` ({r.get('bootimg_build_reason', 'n/a')})",
        "",
        "## Next Focus",
        f"- Focus: `{n.get('focus', 'collect-more-data')}`",
        f"- Reason: `{n.get('reason', 'n/a')}`",
        f"- Consistency Errors: `{d.get('errors', '') or 'none'}`",
        "",
        "## Suggested First Files",
        "- `runtime-validation-summary.md`",
        "- `runtime-validation-input.md`",
        "- `runtime-validation-result.txt`",
        "- `phase2-report.txt`",
        "- `status-badge-line.txt`",
        "- `action-validation-checklist.md`",
        "- `build-error-summary.txt`",
        "- `anykernel-info.txt`",
    ]

    if next_action == 'prepare-release-bootimg':
        md.extend([
            "- `bootimg-info.txt`",
            "- `bootimg-build.txt`",
        ])

    if next_action == 'integrate-drivers-phase3':
        md.append("- `driver-integration-status.txt`")
        md.append("- `Porting/Reference-Drivers-Analysis.md`")
        md.append("- `Porting/OfficialRom-Umi-Os1.0.5.0-Analysis.md`")

    if r.get('runtime_ready', 'no') == 'yes':
        md.append("- `action-validation-checklist.md`")
        md.append("- `runtime-validation-summary.md`")

    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
