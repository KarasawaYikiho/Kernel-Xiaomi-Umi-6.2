#!/usr/bin/env python3
from __future__ import annotations

from typing import Iterable

ALLOWED_NEXT_ACTION: set[str] = {
    "collect-more-data",
    "fix-defconfig-errors",
    "fix-build-errors",
    "fix-dtb-build-errors",
    "ready-for-action-test",
    "prepare-release-bootimg",
    "fix-anykernel-packaging",
}


def is_nonzero_rc(value: str) -> bool:
    return value not in ("0", "n/a")


def derive_next_action(
    *,
    defconfig_rc: str,
    build_rc: str,
    dtbs_rc: str,
    flash_status: str,
    anykernel_ok: str,
    anykernel_validate_status: str,
    bootimg_status: str,
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

    return next_action


def derive_runtime_ready(next_action: str) -> str:
    return "yes" if next_action == "ready-for-action-test" else "no"
