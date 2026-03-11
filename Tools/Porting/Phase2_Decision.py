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
}


def is_nonzero_rc(value: str) -> bool:
    return value not in ("0", "n/a")


def parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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

    # Packaging/release blockers override compile-stage readiness.
    if bootimg_status in ("missing", "size_mismatch"):
        next_action = "prepare-release-bootimg"
    elif flash_status == "candidate" and (
        anykernel_ok != "yes" or anykernel_validate_status not in ("ok", "unknown")
    ):
        next_action = "fix-anykernel-packaging"

    if next_action == "ready-for-action-test" and driver_integration_status != "complete":
        next_action = "integrate-drivers-phase3"

    return next_action


def derive_runtime_ready(next_action: str) -> str:
    return "yes" if next_action == "ready-for-action-test" else "no"


def derive_next_focus(
    *,
    report_next_action: str,
    build_rc: str,
    dtbs_rc: str,
    flash_status: str,
    anykernel_ok: str,
    anykernel_validate_status: str,
    manifest_hit_ratio: float,
) -> tuple[str, str]:
    # Keep focus semantically pinned to report decision when possible.
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
