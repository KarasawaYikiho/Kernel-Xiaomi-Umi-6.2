#!/usr/bin/env python3
from pathlib import Path

from KvUtils import parse_kv

ART = Path("artifacts")
INP = ART / "runtime-validation-input.md"
OUT = ART / "runtime-validation-result.txt"

ALLOWED = {"PASS", "FAIL", "SKIP", "UNKNOWN"}
ALLOWED_BOOT_METHODS = {"fastboot_boot", "anykernel", "unknown", ""}
PREFLIGHT_ORDER = [
    "preflight.bootloader_unlocked",
    "preflight.rom_matches_baseline",
    "preflight.stock_partitions_backed_up",
    "preflight.fastboot_boot_supported",
    "preflight.current_slot_recorded",
    "preflight.rollback_package_ready",
]
CHECK_ORDER = [
    "check.temporary_boot",
    "check.first_boot",
    "check.uname",
    "check.connectivity",
    "check.audio",
    "check.camera",
    "check.touch",
    "check.charging",
    "check.thermal",
    "check.idle_stability",
    "check.light_load_stability",
]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    if not INP.exists():
        OUT.write_text(
            "\n".join(
                [
                    "status=missing_input",
                    "overall=UNKNOWN",
                    "pass_count=0",
                    "fail_count=0",
                    "skip_count=0",
                    "unknown_count=0",
                    "failed_step=",
                    "notes=",
                    "dmesg=",
                    "logcat=",
                    "pstore=",
                    "preflight_count=0",
                    "preflight_pass_count=0",
                    "preflight_complete=no",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {OUT}: missing_input")
        return 0

    kv = parse_kv(INP)
    normalized: dict[str, str] = {}
    invalid: list[str] = []

    for key in PREFLIGHT_ORDER + CHECK_ORDER:
        value = kv.get(key, "UNKNOWN").strip().upper()
        if value not in ALLOWED:
            invalid.append(f"{key}:{value}")
            value = "UNKNOWN"
        normalized[key] = value

    overall = kv.get("meta.overall", "UNKNOWN").strip().upper()
    if overall not in ALLOWED:
        invalid.append(f"meta.overall:{overall}")
        overall = "UNKNOWN"

    preflight_pass_count = sum(1 for k in PREFLIGHT_ORDER if normalized[k] == "PASS")
    preflight_fail_count = sum(1 for k in PREFLIGHT_ORDER if normalized[k] == "FAIL")
    preflight_unknown_count = sum(1 for k in PREFLIGHT_ORDER if normalized[k] == "UNKNOWN")
    preflight_complete = (
        "yes"
        if preflight_pass_count == len(PREFLIGHT_ORDER)
        and preflight_fail_count == 0
        and preflight_unknown_count == 0
        else "no"
    )

    pass_count = sum(1 for k in CHECK_ORDER if normalized[k] == "PASS")
    fail_count = sum(1 for k in CHECK_ORDER if normalized[k] == "FAIL")
    skip_count = sum(1 for k in CHECK_ORDER if normalized[k] == "SKIP")
    unknown_count = sum(1 for k in CHECK_ORDER if normalized[k] == "UNKNOWN")

    boot_method = kv.get("meta.boot_method", "fastboot_boot").strip().lower()
    if boot_method not in ALLOWED_BOOT_METHODS:
        invalid.append(f"meta.boot_method:{boot_method}")
        boot_method = "unknown"

    patched_boot_image = kv.get("meta.patched_boot_image", "").strip()

    first_failed_preflight = next((k for k in PREFLIGHT_ORDER if normalized[k] == "FAIL"), "")
    first_failed = first_failed_preflight or next((k for k in CHECK_ORDER if normalized[k] == "FAIL"), "")
    failed_step = kv.get("meta.failed_step", "").strip() or first_failed

    status = "ok" if not invalid else "invalid_input"
    if first_failed_preflight:
        status = "preflight_failed"
        overall = "FAIL"
    if overall == "UNKNOWN" and pass_count == 0 and fail_count == 0 and skip_count == 0:
        status = "awaiting_device_validation" if not invalid else "invalid_input"

    lines = [
        f"status={status}",
        f"overall={overall}",
        f"boot_method={boot_method}",
        f"patched_boot_image={patched_boot_image}",
        f"stock_boot_backup_sha256={kv.get('meta.stock_boot_backup_sha256', '').strip()}",
        f"stock_dtbo_backup_sha256={kv.get('meta.stock_dtbo_backup_sha256', '').strip()}",
        f"stock_vbmeta_backup_sha256={kv.get('meta.stock_vbmeta_backup_sha256', '').strip()}",
        f"stock_vbmeta_system_backup_sha256={kv.get('meta.stock_vbmeta_system_backup_sha256', '').strip()}",
        f"preflight_count={len(PREFLIGHT_ORDER)}",
        f"preflight_pass_count={preflight_pass_count}",
        f"preflight_fail_count={preflight_fail_count}",
        f"preflight_unknown_count={preflight_unknown_count}",
        f"preflight_complete={preflight_complete}",
        f"pass_count={pass_count}",
        f"fail_count={fail_count}",
        f"skip_count={skip_count}",
        f"unknown_count={unknown_count}",
        f"failed_step={failed_step}",
        f"notes={kv.get('meta.notes', '').strip()}",
        f"dmesg={kv.get('meta.dmesg', '').strip()}",
        f"logcat={kv.get('meta.logcat', '').strip()}",
        f"pstore={kv.get('meta.pstore', '').strip()}",
        f"invalid={','.join(invalid)}",
    ]
    for key in PREFLIGHT_ORDER:
        lines.append(f"{key}={normalized[key]}")
    for key in CHECK_ORDER:
        lines.append(f"{key}={normalized[key]}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
