#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

import BuildDriverIntegrationStatus
import BuildPhase2Report
import BuildPlanProgress
import BuildRomAlignmentStatus
import BuildRuntimeValidationSummary
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
    shutil.copy(ROOT / "Porting-Plan.md", tmp / "Porting-Plan.md")
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
        "python3 Tools/Porting/ValidatePhase2Report.py",
    )


def main() -> int:
    tests = [
        test_plan_progress_parses_all_phase_checklists,
        test_phase2_report_emits_hard_gates,
        test_runtime_summary_splits_phase_blockers,
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
