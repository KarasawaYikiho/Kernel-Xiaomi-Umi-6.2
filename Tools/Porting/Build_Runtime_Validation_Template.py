#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "runtime-validation-input.md"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Runtime Validation Input",
        "",
        "Fill this file after device-side validation. Keep each result on one line.",
        "Use: PASS / FAIL / SKIP / UNKNOWN",
        "",
        "meta.overall=UNKNOWN",
        "meta.failed_step=",
        "meta.notes=",
        "meta.dmesg=",
        "meta.logcat=",
        "",
        "check.boot_flash=UNKNOWN",
        "check.first_boot=UNKNOWN",
        "check.uname=UNKNOWN",
        "check.connectivity=UNKNOWN",
        "check.audio=UNKNOWN",
        "check.camera=UNKNOWN",
        "check.touch=UNKNOWN",
        "check.charging=UNKNOWN",
        "check.thermal=UNKNOWN",
        "check.idle_stability=UNKNOWN",
        "check.light_load_stability=UNKNOWN",
        "",
        "# Example:",
        "# meta.overall=FAIL",
        "# meta.failed_step=check.audio",
        "# meta.notes=speaker silent but bluetooth audio ok",
        "# meta.dmesg=attached in chat",
        "# meta.logcat=attached in chat",
        "# check.boot_flash=PASS",
        "# check.first_boot=PASS",
        "# check.uname=PASS",
        "# check.connectivity=PASS",
        "# check.audio=FAIL",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
