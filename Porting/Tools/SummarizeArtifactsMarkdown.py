#!/usr/bin/env python3
from pathlib import Path

from KvUtils import parse_kv
from Phase2Decision import driver_integration_allows_runtime

ART = Path("artifacts")
OUT = ART / "artifact-summary.md"


def append_unique(md: list[str], items: list[str]) -> None:
    seen = set(md)
    for item in items:
        if item in seen:
            continue
        md.append(item)
        seen.add(item)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    r = parse_kv(ART / "phase2-report.txt")
    n = parse_kv(ART / "next-focus.txt")
    c = parse_kv(ART / "artifact-completeness.txt")
    d = parse_kv(ART / "decision-consistency.txt")
    rv = parse_kv(ART / "runtime-validation-result.txt")

    next_action = r.get("next_action", "")
    runtime_gate = (
        "ready"
        if r.get("runtime_ready", "no") == "yes"
        and driver_integration_allows_runtime(
            r.get("driver_integration_status", "pending"),
            r.get("driver_integration_pending", ""),
        )
        and d.get("status", "unknown") in ("ok", "unknown")
        else "blocked"
    )

    md = [
        "# Phase2 Artifact Summary",
        "",
        f"- Device: `{r.get('device', 'unknown')}`",
        f"- Build RC: `{r.get('build_rc', 'n/a')}` (defconfig `{r.get('defconfig_rc', 'n/a')}`)",
        f"- Flash Status: `{r.get('flash_status', 'unknown')}`",
        f"- Release Status: `{r.get('release_status', 'unknown')}` ({r.get('release_reason', 'n/a')})",
        f"- AnyKernel OK: `{r.get('anykernel_ok', 'no')}` ({r.get('anykernel_reason', 'n/a')})",
        f"- AnyKernel Validate: `{r.get('anykernel_validate_status', 'unknown')}` ({r.get('anykernel_validate_reason', 'n/a')})",
        f"- Manifest Hit Ratio: `{r.get('manifest_hit_ratio', '0.000')}`",
        f"- Artifact Completeness: `{c.get('status', 'unknown')}`",
        f"- Runtime Gate: `{runtime_gate}`",
        f"- Runtime Ready: `{r.get('runtime_ready', 'no')}`",
        f"- Driver Integration: `{r.get('driver_integration_status', 'pending')}` ({r.get('driver_integration_reason', 'n/a')})",
        f"- Driver Follow-ups: `{r.get('driver_integration_pending', '') or 'none'}`",
        f"- Decision Consistency: `{d.get('status', 'unknown')}`",
        f"- Runtime Validation Result: `{rv.get('overall', 'UNKNOWN')}` ({rv.get('status', 'missing_input')})",
        f"- Runtime Validation Failed Step: `{rv.get('failed_step', '') or 'none'}`",
        f"- Boot Image: `{r.get('bootimg_status', 'missing')}` ({r.get('bootimg_reason', 'n/a')}) - release follow-up",
        f"- Boot Image ROM Match: `size={r.get('bootimg_rom_size_match', 'unknown')}` `header={r.get('bootimg_rom_header_version_match', 'unknown')}` `sha256={r.get('bootimg_rom_sha256_match', 'unknown')}`",
        f"- Boot Image Official Reference Gate: `{r.get('bootimg_official_reference_gate', 'no')}` ({r.get('bootimg_official_reference_gate_reasons', '') or 'none'})",
        f"- Boot Image Build: `{r.get('bootimg_build_status', 'unknown')}` ({r.get('bootimg_build_reason', 'n/a')})",
        f"- Fastboot Boot Package: `{'ready' if r.get('release_status', 'unknown') == 'ready' and r.get('bootimg_status', 'missing') == 'ok' and r.get('bootimg_rom_size_match', 'unknown') == 'yes' and r.get('bootimg_rom_header_version_match', 'unknown') == 'yes' and r.get('bootimg_official_reference_gate', 'no') == 'yes' else 'blocked'}`",
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
        "- `bootimg-info.txt`",
    ]

    if next_action == "prepare-release-bootimg":
        append_unique(
            md,
            [
                "- `bootimg-info.txt`",
                "- `bootimg-build.txt`",
            ],
        )

    if next_action == "integrate-drivers-phase3":
        append_unique(
            md,
            [
                "- `driver-integration-status.txt`",
                "- `Porting/ReferenceDriversAnalysis.md`",
                "- `Porting/OfficialRomAnalysis.md`",
            ],
        )

    if n.get("focus", "") == "improve-dtb-manifest-mapping":
        append_unique(
            md,
            [
                "- `target_dtb_manifest.txt`",
                "- `target_dtb_manifest_debug.txt`",
                "- `dtb-postcheck.txt`",
                "- `dtb-miss-analysis.txt`",
            ],
        )

    if r.get("runtime_ready", "no") == "yes":
        append_unique(
            md,
            [
                "- `action-validation-checklist.md`",
                "- `runtime-validation-summary.md`",
            ],
        )

    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
