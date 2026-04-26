#!/usr/bin/env python3
from __future__ import annotations

from Phase2Decision import (
    derive_next_action,
    derive_next_focus,
    derive_runtime_ready,
    driver_integration_runtime_blockers,
)


def expect(name: str, actual: str, expected: str) -> None:
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")


def main() -> int:
    cases = [
        (
            "runtime-ready-with-rom-followups",
            dict(
                defconfig_rc="0",
                build_rc="0",
                dtbs_rc="0",
                flash_status="candidate",
                anykernel_ok="yes",
                anykernel_validate_status="ok",
                bootimg_status="ok",
                driver_integration_status="partial",
                driver_integration_pending="rom_boot_chain_consistency,rom_dynamic_partition_baseline",
                rom_alignment_status="complete",
                rom_alignment_pending="",
                runtime_validation_overall="UNKNOWN",
            ),
            "ready-for-action-test",
            "yes",
        ),
        (
            "runtime-ready-with-rom-aligned-bootimg-primary-path",
            dict(
                defconfig_rc="n/a",
                build_rc="n/a",
                dtbs_rc="n/a",
                flash_status="not_ready",
                anykernel_ok="no",
                anykernel_validate_status="missing",
                bootimg_status="ok",
                driver_integration_status="complete",
                driver_integration_pending="",
                rom_alignment_status="complete",
                rom_alignment_pending="",
                runtime_validation_overall="UNKNOWN",
            ),
            "ready-for-action-test",
            "yes",
        ),
        (
            "runtime-blocked-by-real-driver-gap",
            dict(
                defconfig_rc="0",
                build_rc="0",
                dtbs_rc="0",
                flash_status="candidate",
                anykernel_ok="yes",
                anykernel_validate_status="ok",
                bootimg_status="ok",
                driver_integration_status="partial",
                driver_integration_pending="display_pipeline",
                rom_alignment_status="complete",
                rom_alignment_pending="",
                runtime_validation_overall="UNKNOWN",
            ),
            "integrate-drivers-phase3",
            "no",
        ),
        (
            "runtime-fail-routes-to-analysis",
            dict(
                defconfig_rc="0",
                build_rc="0",
                dtbs_rc="0",
                flash_status="candidate",
                anykernel_ok="yes",
                anykernel_validate_status="ok",
                bootimg_status="ok",
                driver_integration_status="complete",
                driver_integration_pending="",
                rom_alignment_status="complete",
                rom_alignment_pending="",
                runtime_validation_overall="FAIL",
            ),
            "analyze-runtime-failure",
            "no",
        ),
        (
            "runtime-pass-routes-to-release-bootimg",
            dict(
                defconfig_rc="0",
                build_rc="0",
                dtbs_rc="0",
                flash_status="candidate",
                anykernel_ok="yes",
                anykernel_validate_status="ok",
                bootimg_status="missing",
                driver_integration_status="complete",
                driver_integration_pending="",
                rom_alignment_status="pending",
                rom_alignment_pending="bootimg_release_packaging",
                runtime_validation_overall="PASS",
            ),
            "prepare-release-bootimg",
            "no",
        ),
        (
            "runtime-pass-routes-to-alignment-followup",
            dict(
                defconfig_rc="0",
                build_rc="0",
                dtbs_rc="0",
                flash_status="candidate",
                anykernel_ok="yes",
                anykernel_validate_status="ok",
                bootimg_status="ok",
                driver_integration_status="partial",
                driver_integration_pending="rom_boot_chain_consistency",
                rom_alignment_status="partial",
                rom_alignment_pending="rom_dtbo_consistency",
                runtime_validation_overall="PASS",
            ),
            "prepare-release-bootimg",
            "no",
        ),
        (
            "missing-bootimg-before-runtime-pass",
            dict(
                defconfig_rc="0",
                build_rc="0",
                dtbs_rc="0",
                flash_status="unknown",
                anykernel_ok="no",
                anykernel_validate_status="unknown",
                bootimg_status="missing",
                driver_integration_status="pending",
                driver_integration_pending="",
                rom_alignment_status="pending",
                rom_alignment_pending="bootimg_release_packaging",
                runtime_validation_overall="UNKNOWN",
            ),
            "prepare-release-bootimg",
            "no",
        ),
        (
            "invalid-bootimg-format-after-runtime-pass",
            dict(
                defconfig_rc="0",
                build_rc="0",
                dtbs_rc="0",
                flash_status="candidate",
                anykernel_ok="yes",
                anykernel_validate_status="ok",
                bootimg_status="invalid_format",
                driver_integration_status="complete",
                driver_integration_pending="",
                rom_alignment_status="pending",
                rom_alignment_pending="bootimg_release_packaging",
                runtime_validation_overall="PASS",
            ),
            "prepare-release-bootimg",
            "no",
        ),
        (
            "reference-mismatch-routes-to-release-bootimg",
            dict(
                defconfig_rc="0",
                build_rc="0",
                dtbs_rc="0",
                flash_status="candidate",
                anykernel_ok="yes",
                anykernel_validate_status="ok",
                bootimg_status="reference_mismatch",
                driver_integration_status="complete",
                driver_integration_pending="",
                rom_alignment_status="pending",
                rom_alignment_pending="bootimg_release_packaging",
                runtime_validation_overall="UNKNOWN",
            ),
            "prepare-release-bootimg",
            "no",
        ),
        (
            "runtime-ready-blocked-by-rom-alignment-gap",
            dict(
                defconfig_rc="0",
                build_rc="0",
                dtbs_rc="0",
                flash_status="candidate",
                anykernel_ok="yes",
                anykernel_validate_status="ok",
                bootimg_status="ok",
                driver_integration_status="complete",
                driver_integration_pending="",
                rom_alignment_status="partial",
                rom_alignment_pending="rom_dtbo_consistency",
                runtime_validation_overall="UNKNOWN",
            ),
            "prepare-release-bootimg",
            "no",
        ),
    ]

    for name, kwargs, expected_action, expected_runtime in cases:
        actual_action = derive_next_action(**kwargs)
        actual_runtime = derive_runtime_ready(actual_action)
        expect(f"{name}.next_action", actual_action, expected_action)
        expect(f"{name}.runtime_ready", actual_runtime, expected_runtime)

    blockers = driver_integration_runtime_blockers(
        driver_integration_status="partial",
        driver_integration_pending="rom_boot_chain_consistency,display_pipeline",
    )
    expect("runtime_blockers.filter", ",".join(blockers), "display_pipeline")

    focus_cases = [
        (
            "local-rom-baseline-without-build-context",
            (
                "collect-more-data",
                "partial",
                "no",
                "n/a",
                "n/a",
                "not_ready",
                "no",
                "missing",
                0.0,
                "pending",
                "bootimg_release_packaging",
                "UNKNOWN",
                "",
            ),
            ("prepare-release-bootimg", "rom_alignment_incomplete"),
        ),
        (
            "candidate-with-valid-packaging-requests-device-test",
            (
                "ready-for-action-test",
                "ok",
                "yes",
                "0",
                "0",
                "candidate",
                "yes",
                "ok",
                0.75,
                "complete",
                "",
                "UNKNOWN",
                "",
            ),
            ("request-action-validation", "report_next_action"),
        ),
        (
            "rom-aligned-bootimg-primary-path-requests-device-test",
            (
                "ready-for-action-test",
                "partial",
                "no",
                "n/a",
                "n/a",
                "not_ready",
                "no",
                "missing",
                0.0,
                "complete",
                "",
                "UNKNOWN",
                "",
            ),
            ("request-action-validation", "report_next_action"),
        ),
        (
            "real-dtb-gap-still-surfaces-when-build-context-exists",
            (
                "collect-more-data",
                "ok",
                "yes",
                "0",
                "0",
                "not_ready",
                "no",
                "missing",
                0.0,
                "complete",
                "",
                "UNKNOWN",
                "",
            ),
            ("improve-dtb-manifest-mapping", "low_manifest_hit_ratio"),
        ),
        (
            "rom-alignment-gap-surfaces-before-device-test",
            (
                "collect-more-data",
                "ok",
                "yes",
                "0",
                "0",
                "candidate",
                "yes",
                "ok",
                0.75,
                "partial",
                "rom_dtbo_consistency",
                "UNKNOWN",
                "",
            ),
            ("prepare-release-bootimg", "rom_alignment_incomplete"),
        ),
    ]

    for name, args, expected in focus_cases:
        actual = derive_next_focus(
            report_next_action=args[0],
            artifact_completeness=args[1],
            build_context_present=args[2],
            build_rc=args[3],
            dtbs_rc=args[4],
            flash_status=args[5],
            anykernel_ok=args[6],
            anykernel_validate_status=args[7],
            manifest_hit_ratio=args[8],
            rom_alignment_status=args[9],
            rom_alignment_pending=args[10],
            runtime_validation_overall=args[11],
            runtime_validation_failed_step=args[12],
        )
        expect(f"{name}.focus", actual[0], expected[0])
        expect(f"{name}.reason", actual[1], expected[1])

    print("decision-flow-selftest=ok")
    print(f"case_count={len(cases) + len(focus_cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
