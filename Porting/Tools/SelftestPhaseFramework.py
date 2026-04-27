#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import BuildDriverIntegrationStatus
import BuildActionValidationChecklist
import BuildStatusBadgeLine
import BuildPhase2Report
import BuildPlanProgress
import BuildRomAlignmentStatus
import BuildRuntimeValidationSummary
import BuildRuntimeValidationTemplate
import CollectMetricsJson
import ParseRuntimeValidationInput
import SummarizeArtifactsMarkdown
import ValidatePhase2Report


ROOT = Path(__file__).resolve().parents[2]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def kv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        out[key] = value
    return out


def expect(name: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")


def expect_contains(name: str, text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"{name}: missing {needle!r}")


def setup_common(tmp: Path) -> None:
    shutil.copy(ROOT / "PortingPlan.md", tmp / "PortingPlan.md")
    write(
        tmp / "Porting" / "ReferenceDriversAnalysis.md",
        """
        # Reference Driver Analysis
        Primary focus bucket: `cam_sensor_module`
        """,
    )
    write(
        tmp / "Porting" / "OfficialRomAnalysis.md",
        """
        # Official ROM Analysis
        dynamic partitions are present
        """,
    )
    write(
        tmp / "artifacts" / "phase2-report.txt",
        """
        phase2_report=1
        device=umi
        defconfig_rc=0
        build_rc=0
        dtbs_rc=2
        flash_status=candidate
        release_status=ready
        anykernel_ok=yes
        anykernel_validate_status=ok
        bootimg_status=ok
        bootimg_official_reference_gate=yes
        bootimg_rom_size_match=yes
        bootimg_rom_header_version_match=yes
        driver_integration_status=partial
        driver_integration_pending=camera_isp_path
        rom_alignment_status=partial
        rom_alignment_pending=dtb_target_coverage,runtime_validation_official_rom
        runtime_validation_overall=UNKNOWN
        next_action=fix-dtb-build-errors
        runtime_ready=no
        """,
    )


def test_plan_progress_parses_all_phase_checklists(tmp: Path) -> None:
    setup_common(tmp)
    BuildPlanProgress.main()
    progress = kv(tmp / "artifacts" / "plan-progress.txt")
    expect("phase2 total", progress.get("phase_2_checklist_total"), "10")
    expect("phase3 next", progress.get("phase_3_next_gap"), "analyze_camera_isp_path_as_the_first_usability_blocker")
    expect("phase4 blocked", progress.get("phase_4_blocked_by"), "phase_2,phase_3")


def test_plan_progress_uses_current_phase2_evidence(tmp: Path) -> None:
    setup_common(tmp)
    write(
        tmp / "artifacts" / "phase2-report.txt",
        """
        phase2_report=1
        phase2_report_state=ready
        defconfig_rc=0
        build_rc=0
        dtbs_rc=0
        phase2_complete=yes
        phase2_blockers=
        manifest_wanted=4
        manifest_miss=0
        bootimg_status=ok
        bootimg_official_reference_gate=yes
        rom_alignment_pending=runtime_validation_official_rom
        """,
    )
    BuildPlanProgress.main()
    progress = kv(tmp / "artifacts" / "plan-progress.txt")
    expect(
        "workflow source tree",
        progress.get("checklist_build_workflow_targets_the_checked_out_kernel_source_tree_status"),
        "complete",
    )
    expect(
        "dtb manifest mismatch",
        progress.get("checklist_resolve_dtb_manifest_to_build_mismatches_status"),
        "complete",
    )
    expect(
        "dtbs evidence",
        progress.get("checklist_local_evidence_confirms_dtbs_rc_0_status"),
        "complete",
    )
    expect(
        "phase2 blockers cleared",
        progress.get("checklist_phase_2_report_has_no_required_blockers_status"),
        "complete",
    )


def test_phase2_report_emits_hard_gates(tmp: Path) -> None:
    setup_common(tmp)
    write(tmp / "artifacts" / "build-exit.txt", "defconfig_rc=0\nbuild_rc=0\ndtbs_rc=2")
    write(tmp / "artifacts" / "flash-readiness.txt", "status=candidate\nrelease_status=ready")
    write(tmp / "artifacts" / "dtb-postcheck.txt", "wanted=4\nhit=0\nmiss=4\nhit_ratio=0.000")
    write(tmp / "artifacts" / "anykernel-info.txt", "anykernel_ok=yes")
    write(tmp / "artifacts" / "anykernel-validate.txt", "status=ok")
    write(tmp / "artifacts" / "bootimg-info.txt", "status=ok\nofficial_reference_gate=yes")
    write(tmp / "artifacts" / "driver-integration-status.txt", "status=partial\npending=camera_isp_path")
    write(tmp / "artifacts" / "rom-alignment-status.txt", "status=partial\npending=dtb_target_coverage,runtime_validation_official_rom")
    write(tmp / "artifacts" / "plan-progress.txt", "phase_2_status=in_progress\nphase_3_status=pending\nphase_4_status=pending")
    BuildPhase2Report.main()
    report = kv(tmp / "artifacts" / "phase2-report.txt")
    expect("phase2 report state", report.get("phase2_report_state"), "not_ready")
    expect("dtbs gate", report.get("phase2_dtbs_gate"), "fail")
    expect("phase2 complete", report.get("phase2_complete"), "no")
    expect("phase2 blockers", report.get("phase2_blockers"), "dtbs_rc=2")


def test_runtime_summary_splits_phase_blockers(tmp: Path) -> None:
    setup_common(tmp)
    write(tmp / "artifacts" / "decision-consistency.txt", "status=ok")
    write(tmp / "artifacts" / "next-focus.txt", "focus=fix-dtb-errors\nreason=dtb_build_failed")
    write(tmp / "artifacts" / "run-meta.txt", "device=umi\nrun_number=local\nsha=test")
    write(tmp / "artifacts" / "runtime-validation-result.txt", "overall=UNKNOWN\nstatus=missing_input")
    BuildRuntimeValidationSummary.main()
    summary = read(tmp / "artifacts" / "runtime-validation-summary.md")
    expect_contains("phase2 section", summary, "## Phase 2 Blockers")
    expect_contains("phase3 section", summary, "## Phase 3 Usability Blockers")
    expect_contains("phase4 section", summary, "## Phase 4 Runtime Validation")


def test_runtime_guidance_uses_fastboot_boot_route(tmp: Path) -> None:
    setup_common(tmp)
    write(
        tmp / "artifacts" / "phase2-report.txt",
        """
        phase2_report=1
        device=umi
        phase2_complete=yes
        phase2_blockers=
        defconfig_rc=0
        build_rc=0
        dtbs_rc=0
        flash_status=unknown
        release_status=ready
        bootimg_status=ok
        bootimg_rom_size_match=yes
        bootimg_rom_header_version_match=yes
        bootimg_official_reference_gate=yes
        anykernel_ok=yes
        anykernel_validate_status=ok
        driver_integration_status=partial
        driver_integration_pending=camera_isp_path,camera_sensor_module
        runtime_ready=no
        next_action=integrate-drivers-phase3
        runtime_validation_boot_method=fastboot_boot
        """,
    )
    write(tmp / "artifacts" / "decision-consistency.txt", "status=ok")
    write(tmp / "artifacts" / "next-focus.txt", "focus=integrate-drivers-phase3\nreason=phase3_pending")
    write(tmp / "artifacts" / "run-meta.txt", "device=umi\nrun_number=local\nsha=test")
    write(
        tmp / "artifacts" / "runtime-validation-result.txt",
        "overall=UNKNOWN\nstatus=awaiting_device_validation\nboot_method=fastboot_boot",
    )
    BuildActionValidationChecklist.main()
    BuildRuntimeValidationSummary.main()
    checklist = read(tmp / "artifacts" / "action-validation-checklist.md")
    summary = read(tmp / "artifacts" / "runtime-validation-summary.md")
    if "Magisk-patched boot path as the primary" in checklist + summary:
        raise AssertionError("runtime guidance still promotes Magisk as the primary route")
    if "flash_status=unknown" in summary:
        raise AssertionError("fastboot_boot route should not treat flash_status=unknown as a Phase2 blocker")
    expect_contains("checklist fastboot", checklist, "fastboot boot")
    expect_contains("summary fastboot", summary, "fastboot boot")


def test_action_checklist_documents_patcher_agnostic_boot(tmp: Path) -> None:
    setup_common(tmp)
    write(tmp / "artifacts" / "decision-consistency.txt", "status=ok")
    write(tmp / "artifacts" / "run-meta.txt", "device=umi\nrun_number=local\nsha=test")
    BuildActionValidationChecklist.main()
    checklist = read(tmp / "artifacts" / "action-validation-checklist.md")
    for required in [
        "patcher-agnostic",
        "KernelSU",
        "Magisk",
        "official-aligned custom boot",
    ]:
        expect_contains("patcher agnostic checklist", checklist, required)


def test_status_outputs_use_fastboot_boot_package_label(tmp: Path) -> None:
    setup_common(tmp)
    write(tmp / "artifacts" / "decision-consistency.txt", "status=ok")
    write(tmp / "artifacts" / "next-focus.txt", "focus=integrate-drivers-phase3\nreason=phase3_pending")
    write(tmp / "artifacts" / "phase2-report-validate.txt", "status=ok")
    write(tmp / "artifacts" / "runtime-validation-result.txt", "overall=UNKNOWN\nstatus=awaiting_device_validation\nboot_method=fastboot_boot")
    SummarizeArtifactsMarkdown.main()
    BuildStatusBadgeLine.main()
    CollectMetricsJson.main()
    summary = read(tmp / "artifacts" / "artifact-summary.md")
    badge = read(tmp / "artifacts" / "status-badge-line.txt")
    metrics = read(tmp / "artifacts" / "phase2-metrics.json")
    for name, text in {
        "artifact summary": summary,
        "status badge": badge,
        "metrics": metrics,
    }.items():
        if "magisk" in text.lower():
            raise AssertionError(f"{name}: still contains magisk-specific runtime labeling")
    expect_contains("artifact summary fastboot", summary, "Fastboot Boot Package")
    expect_contains("status badge fastboot", badge, "fastboot_boot_package_ready=")
    expect_contains("metrics fastboot", metrics, "fastboot_boot_package_ready")


def test_runtime_validation_template_requires_device_safety_gates(tmp: Path) -> None:
    setup_common(tmp)
    BuildRuntimeValidationTemplate.main()
    template = read(tmp / "artifacts" / "runtime-validation-input.md")
    for required in [
        "preflight.bootloader_unlocked=UNKNOWN",
        "preflight.rom_matches_baseline=UNKNOWN",
        "preflight.stock_partitions_backed_up=UNKNOWN",
        "preflight.fastboot_boot_supported=UNKNOWN",
        "preflight.current_slot_recorded=UNKNOWN",
        "preflight.rollback_package_ready=UNKNOWN",
        "meta.boot_method=fastboot_boot",
        "meta.stock_boot_backup_sha256=",
        "meta.stock_dtbo_backup_sha256=",
        "meta.stock_vbmeta_backup_sha256=",
        "meta.pstore=",
    ]:
        expect_contains("runtime template preflight", template, required)
    if "magisk" in template.lower():
        raise AssertionError("runtime template still contains magisk-specific validation guidance")


def test_runtime_validation_template_migrates_old_magisk_scaffold(tmp: Path) -> None:
    setup_common(tmp)
    write(
        tmp / "artifacts" / "runtime-validation-input.md",
        """
        # Runtime Validation Input

        Fill this file after device-side validation of the fastboot-booted or Magisk-patched boot image. Keep each result on one line.
        meta.overall=UNKNOWN
        meta.boot_method=fastboot_boot
        # meta.patched_boot_image=magisk_patched-28000_abc123.img
        meta.notes=keep this user note
        """,
    )
    BuildRuntimeValidationTemplate.main()
    template = read(tmp / "artifacts" / "runtime-validation-input.md")
    if "magisk" in template.lower():
        raise AssertionError("runtime template migration left magisk-specific scaffold text")
    expect_contains("template note preserved", template, "meta.notes=keep this user note")
    expect_contains("template migrated image example", template, "# meta.patched_boot_image=boot-test-28000_abc123.img")


def test_runtime_validation_parser_tracks_preflight_gates(tmp: Path) -> None:
    setup_common(tmp)
    write(
        tmp / "artifacts" / "runtime-validation-input.md",
        """
        meta.overall=PASS
        meta.boot_method=fastboot_boot
        meta.patched_boot_image=boot-test.img
        meta.stock_boot_backup_sha256=abc
        meta.stock_dtbo_backup_sha256=def
        meta.stock_vbmeta_backup_sha256=123
        meta.pstore=attached
        preflight.bootloader_unlocked=PASS
        preflight.rom_matches_baseline=PASS
        preflight.stock_partitions_backed_up=PASS
        preflight.fastboot_boot_supported=PASS
        preflight.current_slot_recorded=PASS
        preflight.rollback_package_ready=PASS
        check.temporary_boot=PASS
        check.first_boot=PASS
        check.uname=PASS
        check.connectivity=PASS
        check.audio=PASS
        check.camera=SKIP
        check.touch=PASS
        check.charging=PASS
        check.thermal=PASS
        check.idle_stability=PASS
        check.light_load_stability=PASS
        """,
    )
    ParseRuntimeValidationInput.main()
    result = kv(tmp / "artifacts" / "runtime-validation-result.txt")
    expect("runtime parse status", result.get("status"), "ok")
    expect("runtime boot method", result.get("boot_method"), "fastboot_boot")
    expect("preflight total", result.get("preflight_count"), "6")
    expect("preflight pass", result.get("preflight_pass_count"), "6")
    expect("preflight complete", result.get("preflight_complete"), "yes")
    expect("stock boot hash", result.get("stock_boot_backup_sha256"), "abc")
    expect("pstore field", result.get("pstore"), "attached")


def test_runtime_validation_parser_blocks_failed_preflight(tmp: Path) -> None:
    setup_common(tmp)
    write(
        tmp / "artifacts" / "runtime-validation-input.md",
        """
        meta.overall=PASS
        meta.boot_method=fastboot_boot
        preflight.bootloader_unlocked=PASS
        preflight.rom_matches_baseline=FAIL
        preflight.stock_partitions_backed_up=PASS
        preflight.fastboot_boot_supported=PASS
        preflight.current_slot_recorded=PASS
        preflight.rollback_package_ready=PASS
        check.temporary_boot=PASS
        check.first_boot=PASS
        check.uname=PASS
        """,
    )
    ParseRuntimeValidationInput.main()
    result = kv(tmp / "artifacts" / "runtime-validation-result.txt")
    expect("failed preflight status", result.get("status"), "preflight_failed")
    expect("failed preflight overall", result.get("overall"), "FAIL")
    expect("failed preflight step", result.get("failed_step"), "preflight.rom_matches_baseline")


def test_status_reports_emit_phase_ownership(tmp: Path) -> None:
    setup_common(tmp)
    write(tmp / "artifacts" / "driver-integration-manifest.txt", "integrated: base\npending: camera_isp_path")
    write(tmp / "artifacts" / "driver-integration-evidence.txt", "target_tree_present=yes")
    write(tmp / "artifacts" / "driver-integration-manifest-validate.txt", "status=ok")
    BuildDriverIntegrationStatus.main()
    driver = kv(tmp / "artifacts" / "driver-integration-status.txt")
    expect("driver phase", driver.get("phase"), "3")
    expect("driver blocker", driver.get("next_kernel_usability_blocker"), "camera_isp_path")

    write(tmp / "artifacts" / "rom-alignment-manifest.txt", "integrated: bootimg_release_packaging\npending: dtb_target_coverage\npending: runtime_validation_official_rom")
    write(tmp / "artifacts" / "rom-alignment-manifest-validate.txt", "status=ok")
    write(tmp / "artifacts" / "bootimg-info.txt", "status=ok\nflash_ready=yes")
    write(tmp / "artifacts" / "dtb-postcheck.txt", "hit_ratio=0.500")
    write(tmp / "artifacts" / "runtime-validation-result.txt", "overall=UNKNOWN")
    BuildRomAlignmentStatus.main()
    rom = kv(tmp / "artifacts" / "rom-alignment-status.txt")
    expect("rom phase2 pending", rom.get("phase2_pending"), "dtb_target_coverage")
    expect("rom phase4 pending", rom.get("phase4_pending"), "runtime_validation_official_rom")


def test_phase2_report_validation_is_hard_gate(tmp: Path) -> None:
    setup_common(tmp)
    status = ValidatePhase2Report.main()
    result = kv(tmp / "artifacts" / "phase2-report-validate.txt")
    expect("validate status", result.get("status"), "invalid")
    expect("validate exit", status, 2)


def test_rom_workflow_has_final_phase2_gate(tmp: Path) -> None:
    workflow = (ROOT / ".github" / "workflows" / "ROM-Aligned-Umi-Port.yml").read_text(
        encoding="utf-8"
    )
    expect_contains("workflow final gate name", workflow, "Enforce Phase2 gates")
    expect_contains(
        "workflow final gate command",
        workflow,
        "python3 Porting/Tools/ValidatePhase2Report.py",
    )


def main() -> int:
    tests = [
        test_plan_progress_parses_all_phase_checklists,
        test_plan_progress_uses_current_phase2_evidence,
        test_phase2_report_emits_hard_gates,
        test_runtime_summary_splits_phase_blockers,
        test_runtime_guidance_uses_fastboot_boot_route,
        test_action_checklist_documents_patcher_agnostic_boot,
        test_status_outputs_use_fastboot_boot_package_label,
        test_runtime_validation_template_requires_device_safety_gates,
        test_runtime_validation_template_migrates_old_magisk_scaffold,
        test_runtime_validation_parser_tracks_preflight_gates,
        test_runtime_validation_parser_blocks_failed_preflight,
        test_status_reports_emit_phase_ownership,
        test_phase2_report_validation_is_hard_gate,
        test_rom_workflow_has_final_phase2_gate,
    ]
    with tempfile.TemporaryDirectory(prefix="phase-framework-") as tmpdir:
        tmp = Path(tmpdir)
        old_cwd = Path.cwd()
        try:
            os.chdir(tmp)
            for test in tests:
                test(tmp)
        finally:
            os.chdir(old_cwd)
    print("phase-framework-selftest=ok")
    print(f"case_count={len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
