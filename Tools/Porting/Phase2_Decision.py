#!/usr/bin/env python3
from __future__ import annotations

ALLOWED_NEXT_ACTION: set[str] = {
    "collect-more-data",
    "fix-defconfig-errors",
    "fix-build-errors",
    "fix-dtb-build-errors",
    "ready-for-action-test",
    "prepare-release-bootimg",
    "fix-anykernel-packaging",
    "integrate-drivers-phase3",
    "analyze-runtime-failure",
}

DEFAULT_BOOTIMG_REQUIRED_BYTES = 134217728
DEFAULT_BOOTIMG_REQUIRED_BYTES_STR = str(DEFAULT_BOOTIMG_REQUIRED_BYTES)

REPORT_NEXT_TO_FOCUS: dict[str, str] = {
    "fix-defconfig-errors": "fix-defconfig-errors",
    "fix-build-errors": "fix-build-errors",
    "fix-dtb-build-errors": "fix-dtb-errors",
    "fix-anykernel-packaging": "fix-anykernel-packaging",
    "ready-for-action-test": "request-action-validation",
    "prepare-release-bootimg": "prepare-release-bootimg",
    "integrate-drivers-phase3": "integrate-drivers-phase3",
    "analyze-runtime-failure": "analyze-runtime-failure",
}

RUNTIME_SAFE_DRIVER_PENDING: set[str] = {
    "rom_boot_chain_consistency",
    "rom_dtbo_consistency",
    "rom_vbmeta_consistency",
    "rom_dynamic_partition_baseline",
    "partition_baseline_not_confirmed",
    "target_tree_missing_for_driver_validation",
}


def is_nonzero_rc(value: str) -> bool:
    return value not in ("0", "n/a")


def parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def split_csv(value: str) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


def driver_integration_runtime_blockers(
    driver_integration_status: str,
    driver_integration_pending: str = "",
) -> list[str]:
    if driver_integration_status in ("complete", "unknown"):
        return []
    pending = split_csv(driver_integration_pending)
    blocking = [item for item in pending if item not in RUNTIME_SAFE_DRIVER_PENDING]
    if blocking:
        return blocking
    if driver_integration_status == "partial" and pending:
        return []
    return pending or [f"driver_integration_status={driver_integration_status}"]


def driver_integration_allows_runtime(
    driver_integration_status: str,
    driver_integration_pending: str = "",
) -> bool:
    return not driver_integration_runtime_blockers(
        driver_integration_status=driver_integration_status,
        driver_integration_pending=driver_integration_pending,
    )


def derive_next_action(
    *,
    defconfig_rc: str,
    build_rc: str,
    dtbs_rc: str,
    flash_status: str,
    anykernel_ok: str,
    anykernel_validate_status: str,
    bootimg_status: str,
    driver_integration_status: str,
    driver_integration_pending: str = "",
    runtime_validation_overall: str = "UNKNOWN",
) -> str:
    next_action = "collect-more-data"

    if is_nonzero_rc(defconfig_rc):
        next_action = "fix-defconfig-errors"
    elif is_nonzero_rc(build_rc):
        next_action = "fix-build-errors"
    elif is_nonzero_rc(dtbs_rc):
        next_action = "fix-dtb-build-errors"
    elif (
        flash_status == "candidate"
        and anykernel_ok == "yes"
        and anykernel_validate_status in ("ok", "unknown")
    ):
        next_action = "ready-for-action-test"

    if flash_status == "candidate" and (
        anykernel_ok != "yes" or anykernel_validate_status not in ("ok", "unknown")
    ):
        next_action = "fix-anykernel-packaging"

    if next_action == "ready-for-action-test" and not driver_integration_allows_runtime(
        driver_integration_status=driver_integration_status,
        driver_integration_pending=driver_integration_pending,
    ):
        next_action = "integrate-drivers-phase3"

    if runtime_validation_overall == "FAIL":
        next_action = "analyze-runtime-failure"
    elif runtime_validation_overall == "PASS":
        if bootimg_status in ("missing", "size_mismatch", "invalid_format"):
            next_action = "prepare-release-bootimg"
        elif driver_integration_status != "complete" and split_csv(
            driver_integration_pending
        ):
            next_action = "integrate-drivers-phase3"
        else:
            next_action = "collect-more-data"

    if next_action == "collect-more-data" and bootimg_status in (
        "missing",
        "size_mismatch",
        "invalid_format",
    ):
        next_action = "prepare-release-bootimg"

    return next_action


def derive_runtime_ready(next_action: str) -> str:
    return "yes" if next_action == "ready-for-action-test" else "no"


def derive_next_focus(
    *,
    report_next_action: str,
    artifact_completeness: str = "unknown",
    build_context_present: str = "unknown",
    build_rc: str,
    dtbs_rc: str,
    flash_status: str,
    anykernel_ok: str,
    anykernel_validate_status: str,
    manifest_hit_ratio: float,
    runtime_validation_overall: str = "UNKNOWN",
    runtime_validation_failed_step: str = "",
) -> tuple[str, str]:
    if runtime_validation_overall == "FAIL":
        failed = runtime_validation_failed_step or "runtime-validation"
        return "analyze-runtime-failure", f"runtime_validation_failed:{failed}"

    if (
        artifact_completeness == "partial"
        or build_context_present == "no"
        or flash_status == "unknown"
    ) and (
        manifest_hit_ratio <= 0.0
        and anykernel_ok != "yes"
        and anykernel_validate_status == "missing"
        and not is_nonzero_rc(build_rc)
        and not is_nonzero_rc(dtbs_rc)
    ):
        return "collect-more-data", "missing_phase2_artifacts"

    mapped = REPORT_NEXT_TO_FOCUS.get(report_next_action)
    if mapped:
        return mapped, "report_next_action"

    if is_nonzero_rc(build_rc):
        return "fix-build-errors", "core_build_failed"
    if is_nonzero_rc(dtbs_rc):
        return "fix-dtb-errors", "dtb_build_failed"
    if flash_status == "candidate" and anykernel_ok != "yes":
        return "fix-anykernel-packaging", "candidate_without_anykernel"
    if (
        flash_status == "candidate"
        and anykernel_ok == "yes"
        and anykernel_validate_status not in ("ok", "unknown")
    ):
        return "fix-anykernel-packaging", "candidate_with_invalid_anykernel_structure"
    if flash_status == "candidate" and anykernel_ok == "yes":
        return "request-action-validation", "candidate_and_packaging_ok"
    if manifest_hit_ratio < 0.35:
        return "improve-dtb-manifest-mapping", "low_manifest_hit_ratio"

    return "collect-more-data", "default"
