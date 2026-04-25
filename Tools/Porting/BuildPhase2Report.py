#!/usr/bin/env python3
from pathlib import Path

from KvUtils import parse_kv
from Phase2Decision import (
    DEFAULT_BOOTIMG_REQUIRED_BYTES_STR,
    derive_next_action,
    derive_runtime_ready,
)
from PortConfig import get_nested, load_port_config

ART = Path("artifacts")
OUT = ART / "phase2-report.txt"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    summary = parse_kv(ART / "summary.txt")
    pack = parse_kv(ART / "device_bundle" / "pack-info.txt")
    flash = parse_kv(ART / "flash-readiness.txt")
    dtb = parse_kv(ART / "dtb-postcheck.txt")
    anyk = parse_kv(ART / "anykernel-info.txt")
    anyk_val = parse_kv(ART / "anykernel-validate.txt")
    boot = parse_kv(ART / "bootimg-info.txt")
    boot_build = parse_kv(ART / "bootimg-build.txt")
    missa = parse_kv(ART / "dtb-miss-analysis.txt")
    bexit = parse_kv(ART / "build-exit.txt")
    complete = parse_kv(ART / "artifact-completeness.txt")
    driver = parse_kv(ART / "driver-integration-status.txt")
    rom_align = parse_kv(ART / "rom-alignment-status.txt")
    plan = parse_kv(ART / "plan-progress.txt")
    runtime_result = parse_kv(ART / "runtime-validation-result.txt")
    meta = parse_kv(ART / "run-meta.txt")
    manifest_debug = parse_kv(ART / "target_dtb_manifest_debug.txt")
    config = load_port_config()
    meta_device = meta.get("device", "").strip()
    if meta_device.lower() in {"", "unknown", "?", "n/a"}:
        meta_device = ""
    report_device = pack.get(
        "device",
        summary.get(
            "device",
            meta_device
            or get_nested(config, "reference_baseline_device", default="unknown"),
        ),
    )

    # derive a simple decision hint for next step automation
    flash_status = flash.get("status", "unknown")
    anykernel_ok = anyk.get("anykernel_ok", "no")
    hit_ratio = dtb.get("hit_ratio", "0.000")
    def_rc = bexit.get("defconfig_rc", "n/a")
    build_rc = bexit.get("build_rc", "n/a")
    dtbs_rc = bexit.get("dtbs_rc", "n/a")

    anyk_val_status = anyk_val.get("status", "unknown")
    bootimg_status = boot.get("status", "missing")
    bootimg_reference_gate = boot.get("official_reference_gate", "no")
    phase2_blockers: list[str] = []
    if def_rc != "0":
        phase2_blockers.append(f"defconfig_rc={def_rc}")
    if build_rc != "0":
        phase2_blockers.append(f"build_rc={build_rc}")
    if dtbs_rc != "0":
        phase2_blockers.append(f"dtbs_rc={dtbs_rc}")
    if bootimg_status != "ok":
        phase2_blockers.append(f"bootimg_status={bootimg_status}")
    if bootimg_reference_gate != "yes":
        phase2_blockers.append(f"bootimg_official_reference_gate={bootimg_reference_gate}")
    if anyk_val_status != "ok":
        phase2_blockers.append(f"anykernel_validate_status={anyk_val_status}")
    phase2_build_gate = "pass" if def_rc == "0" and build_rc == "0" else "fail"
    phase2_dtbs_gate = "pass" if dtbs_rc == "0" else "fail"
    phase2_rom_gate = "pass" if bootimg_status == "ok" and bootimg_reference_gate == "yes" else "fail"
    phase2_complete = "yes" if not phase2_blockers else "no"
    next_action = derive_next_action(
        defconfig_rc=def_rc,
        build_rc=build_rc,
        dtbs_rc=dtbs_rc,
        flash_status=flash_status,
        anykernel_ok=anykernel_ok,
        anykernel_validate_status=anyk_val_status,
        bootimg_status=boot.get("status", "missing"),
        driver_integration_status=driver.get("status", "pending"),
        driver_integration_pending=driver.get("pending", ""),
        rom_alignment_status=rom_align.get("status", "pending"),
        rom_alignment_pending=rom_align.get("pending", ""),
        runtime_validation_overall=runtime_result.get("overall", "UNKNOWN"),
    )
    runtime_ready = derive_runtime_ready(next_action)
    if phase2_complete != "yes":
        runtime_ready = "no"

    lines = [
        "phase2_report=1",
        f"device={report_device}",
        f"phase2_report_state={'ready' if phase2_complete == 'yes' else 'not_ready'}",
        f"defconfig_rc={bexit.get('defconfig_rc', 'n/a')}",
        f"build_rc={bexit.get('build_rc', 'n/a')}",
        f"dtbs_rc={bexit.get('dtbs_rc', 'n/a')}",
        f"phase2_build_gate={phase2_build_gate}",
        f"phase2_dtbs_gate={phase2_dtbs_gate}",
        f"phase2_rom_gate={phase2_rom_gate}",
        f"phase2_complete={phase2_complete}",
        f"phase2_blockers={','.join(phase2_blockers)}",
        f"dts_copied={summary.get('dts_copied', '0')}",
        f"dts_only_copied={summary.get('dts_only_copied', '0')}",
        f"dtsi_only_copied={summary.get('dtsi_only_copied', '0')}",
        f"bundle_xiaomi_dtb_count={pack.get('bundle_xiaomi_dtb_count', '0')}",
        f"flash_status={flash.get('status', 'unknown')}",
        f"flash_reason={flash.get('reason', 'n/a')}",
        f"release_status={flash.get('release_status', 'unknown')}",
        f"release_reason={flash.get('release_reason', 'n/a')}",
        f"manifest_wanted={dtb.get('wanted', '0')}",
        f"manifest_hit={dtb.get('hit', '0')}",
        f"manifest_miss={dtb.get('miss', '0')}",
        f"manifest_hit_ratio={hit_ratio}",
        f"manifest_source={manifest_debug.get('source', '')}",
        f"manifest_unique_total={manifest_debug.get('unique_total', '0')}",
        f"anykernel_ok={anykernel_ok}",
        f"anykernel_reason={anyk.get('reason', 'n/a')}",
        f"anykernel_has_imagegz={anyk.get('has_imagegz', 'no')}",
        f"anykernel_imagegz_path={anyk.get('imagegz_path', '')}",
        f"anykernel_has_dtb={anyk.get('has_dtb', 'no')}",
        f"anykernel_dtb_source={anyk.get('dtb_source', '')}",
        f"anykernel_template_source={anyk.get('template_source', '')}",
        f"anykernel_validate_status={anyk_val.get('status', 'unknown')}",
        f"anykernel_validate_reason={anyk_val.get('reason', 'n/a')}",
        f"bootimg_status={boot.get('status', 'missing')}",
        f"bootimg_reason={boot.get('reason', 'n/a')}",
        f"bootimg_size_bytes={boot.get('size_bytes', '0')}",
        f"bootimg_required_bytes={boot.get('required_bytes', DEFAULT_BOOTIMG_REQUIRED_BYTES_STR)}",
        f"bootimg_required_bytes_parse={boot.get('required_bytes_parse', 'unknown')}",
        f"bootimg_size_match={boot.get('size_match', 'no')}",
        f"bootimg_rom_expected_size_bytes={boot.get('rom_expected_size_bytes', '')}",
        f"bootimg_rom_expected_sha256={boot.get('rom_expected_sha256', '')}",
        f"bootimg_rom_expected_header_version={boot.get('rom_expected_header_version', '')}",
        f"bootimg_rom_size_match={boot.get('rom_size_match', 'unknown')}",
        f"bootimg_rom_sha256_match={boot.get('rom_sha256_match', 'unknown')}",
        f"bootimg_rom_header_version_match={boot.get('rom_header_version_match', 'unknown')}",
        f"bootimg_official_reference_present={boot.get('official_reference_present', 'no')}",
        f"bootimg_official_reference_gate={boot.get('official_reference_gate', 'no')}",
        f"bootimg_official_reference_gate_reasons={boot.get('official_reference_gate_reasons', '')}",
        f"bootimg_build_source={boot.get('bootimg_build_source', '')}",
        f"bootimg_build_source_ref={boot.get('bootimg_build_source_ref', '')}",
        f"bootimg_build_status={boot_build.get('status', 'unknown')}",
        f"bootimg_build_reason={boot_build.get('reason', 'n/a')}",
        f"bootimg_build_missing={boot_build.get('missing', '')}",
        f"miss_bucket_total={missa.get('bucket_total', '0')}",
        f"miss_top_buckets={missa.get('top_buckets', '')}",
        f"artifact_completeness={complete.get('status', 'unknown')}",
        f"required_missing={complete.get('required_missing', 'n/a')}",
        f"phase2_required_missing={complete.get('phase2_required_missing', 'n/a')}",
        f"build_context_present={complete.get('build_context_present', 'unknown')}",
        f"driver_integration_status={driver.get('status', 'pending')}",
        f"driver_integration_reason={driver.get('reason', 'n/a')}",
        f"driver_integration_pending={driver.get('pending', '')}",
        f"rom_alignment_status={rom_align.get('status', 'pending')}",
        f"rom_alignment_reason={rom_align.get('reason', 'n/a')}",
        f"rom_alignment_pending={rom_align.get('pending', '')}",
        f"plan_present={plan.get('plan_present', 'no')}",
        f"plan_phase_0_status={plan.get('phase_0_status', 'unknown')}",
        f"plan_phase_1_status={plan.get('phase_1_status', 'unknown')}",
        f"plan_phase_2_status={plan.get('phase_2_status', 'unknown')}",
        f"plan_phase_3_status={plan.get('phase_3_status', 'unknown')}",
        f"plan_phase_4_status={plan.get('phase_4_status', 'unknown')}",
        f"plan_phase_2_checklist_total={plan.get('phase_2_checklist_total', '0')}",
        f"plan_phase_2_checklist_completed={plan.get('phase_2_checklist_completed', '0')}",
        f"plan_phase_2_checklist_remaining={plan.get('phase_2_checklist_remaining', '0')}",
        f"plan_phase_2_next_gap={plan.get('phase_2_next_gap', '')}",
        f"runtime_validation_status={runtime_result.get('status', 'missing_input')}",
        f"runtime_validation_overall={runtime_result.get('overall', 'UNKNOWN')}",
        f"runtime_validation_boot_method={runtime_result.get('boot_method', 'unknown')}",
        f"runtime_validation_patched_boot_image={runtime_result.get('patched_boot_image', '')}",
        f"runtime_validation_failed_step={runtime_result.get('failed_step', '')}",
        f"runtime_validation_pass_count={runtime_result.get('pass_count', '0')}",
        f"runtime_validation_fail_count={runtime_result.get('fail_count', '0')}",
        f"runtime_validation_unknown_count={runtime_result.get('unknown_count', '0')}",
        f"next_action={next_action}",
        f"runtime_ready={runtime_ready}",
    ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
