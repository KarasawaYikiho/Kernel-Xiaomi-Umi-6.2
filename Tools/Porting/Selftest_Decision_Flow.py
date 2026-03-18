#!/usr/bin/env python3
from __future__ import annotations

from Phase2_Decision import derive_next_action, derive_runtime_ready, driver_integration_runtime_blockers


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
                runtime_validation_overall="PASS",
            ),
            "integrate-drivers-phase3",
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

    print("decision-flow-selftest=ok")
    print(f"case_count={len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
