#!/usr/bin/env python3
from pathlib import Path

from KvUtils import parse_kv

ART = Path("artifacts")
INP = ART / "runtime-validation-input.md"
OUT = ART / "runtime-validation-result.txt"

ALLOWED = {"PASS", "FAIL", "SKIP", "UNKNOWN"}
ALLOWED_BOOT_METHODS = {"magisk_patched_boot", "anykernel", "unknown", ""}
CHECK_ORDER = [
    "check.boot_flash",
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

    for key in CHECK_ORDER:
        value = kv.get(key, "UNKNOWN").strip().upper()
        if value not in ALLOWED:
            invalid.append(f"{key}:{value}")
            value = "UNKNOWN"
        normalized[key] = value

    overall = kv.get("meta.overall", "UNKNOWN").strip().upper()
    if overall not in ALLOWED:
        invalid.append(f"meta.overall:{overall}")
        overall = "UNKNOWN"

    pass_count = sum(1 for k in CHECK_ORDER if normalized[k] == "PASS")
    fail_count = sum(1 for k in CHECK_ORDER if normalized[k] == "FAIL")
    skip_count = sum(1 for k in CHECK_ORDER if normalized[k] == "SKIP")
    unknown_count = sum(1 for k in CHECK_ORDER if normalized[k] == "UNKNOWN")

    boot_method = kv.get("meta.boot_method", "magisk_patched_boot").strip().lower()
    if boot_method not in ALLOWED_BOOT_METHODS:
        invalid.append(f"meta.boot_method:{boot_method}")
        boot_method = "unknown"

    patched_boot_image = kv.get("meta.patched_boot_image", "").strip()

    first_failed = next((k for k in CHECK_ORDER if normalized[k] == "FAIL"), "")
    failed_step = kv.get("meta.failed_step", "").strip() or first_failed

    status = "ok" if not invalid else "invalid_input"
    if overall == "UNKNOWN" and pass_count == 0 and fail_count == 0 and skip_count == 0:
        status = "awaiting_device_validation" if not invalid else "invalid_input"

    lines = [
        f"status={status}",
        f"overall={overall}",
        f"boot_method={boot_method}",
        f"patched_boot_image={patched_boot_image}",
        f"pass_count={pass_count}",
        f"fail_count={fail_count}",
        f"skip_count={skip_count}",
        f"unknown_count={unknown_count}",
        f"failed_step={failed_step}",
        f"notes={kv.get('meta.notes', '').strip()}",
        f"dmesg={kv.get('meta.dmesg', '').strip()}",
        f"logcat={kv.get('meta.logcat', '').strip()}",
        f"invalid={','.join(invalid)}",
    ]
    for key in CHECK_ORDER:
        lines.append(f"{key}={normalized[key]}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
