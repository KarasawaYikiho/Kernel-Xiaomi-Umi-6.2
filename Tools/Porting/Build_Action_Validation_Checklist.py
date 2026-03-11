#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "action-validation-checklist.md"


def parse_kv(path: Path) -> dict[str, str]:
    kv: dict[str, str] = {}
    if not path.exists():
        return kv
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return kv


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    report = parse_kv(ART / "phase2-report.txt")
    meta = parse_kv(ART / "run-meta.txt")

    device = report.get("device", meta.get("device", "umi"))
    run_no = meta.get("run_number", "?")
    sha = meta.get("sha", "")
    next_action = report.get("next_action", "collect-more-data")
    runtime_ready = report.get("runtime_ready", "no")
    bootimg_status = report.get("bootimg_status", "missing")
    bootimg_build_status = report.get("bootimg_build_status", "unknown")
    bootimg_build_missing = report.get("bootimg_build_missing", "")
    bootimg_size = report.get("bootimg_size_bytes", "0")
    bootimg_required = report.get("bootimg_required_bytes", "268435456")
    blockers = []
    if report.get("defconfig_rc", "n/a") not in ("0", "n/a"):
        blockers.append(f"defconfig_rc={report.get('defconfig_rc', 'n/a')}")
    if report.get("build_rc", "n/a") not in ("0", "n/a"):
        blockers.append(f"build_rc={report.get('build_rc', 'n/a')}")
    if report.get("dtbs_rc", "n/a") not in ("0", "n/a"):
        blockers.append(f"dtbs_rc={report.get('dtbs_rc', 'n/a')}")
    if report.get("anykernel_ok", "no") != "yes":
        blockers.append("anykernel_ok!=yes")
    if report.get("anykernel_validate_status", "unknown") not in ("ok", "unknown"):
        blockers.append(f"anykernel_validate_status={report.get('anykernel_validate_status', 'unknown')}")
    if bootimg_status != "ok":
        blockers.append(f"bootimg_status={bootimg_status}")
    if bootimg_build_status not in ("ok", "unknown"):
        blockers.append(f"bootimg_build_status={bootimg_build_status}")
    if bootimg_build_missing:
        blockers.append(f"bootimg_build_missing={bootimg_build_missing}")

    md = [
        "# Phase2 Runtime Validation Checklist",
        "",
        f"- Device: `{device}`",
        f"- Run: `{run_no}`",
        f"- SHA: `{sha}`",
        f"- next_action: `{next_action}`",
        f"- runtime_ready: `{runtime_ready}`",
        f"- bootimg_status: `{bootimg_status}`",
        f"- bootimg_build_status: `{bootimg_build_status}`",
        f"- bootimg_size_bytes: `{bootimg_size}`",
        f"- bootimg_required_bytes: `{bootimg_required}`",
        "",
        "## Decision",
        "- [ ] If `runtime_ready=yes`, proceed with device runtime validation now.",
        "- [ ] If `runtime_ready=no`, stop and fix report blockers first.",
        "",
    ]

    if blockers:
        md.extend([
            "## Blockers (from phase2-report)",
            *[f"- {b}" for b in blockers],
            "",
        ])

    md.extend([
        "## Pre-check",
        "- [ ] Confirm battery >= 50% and USB debugging available.",
        "- [ ] Confirm bootloader/unlock state and recovery path prepared.",
        "- [ ] Keep previous known-good boot image for rollback.",
        "",
        "## Flash & Boot",
        "- [ ] Flash `AnyKernel3-umi-candidate.zip` in recovery/fastboot flow.",
        "- [ ] First boot completes without bootloop (wait 3-5 min).",
        "- [ ] `adb shell uname -a` returns expected kernel build.",
        "",
        "## Smoke Tests",
        "- [ ] Wi-Fi/BT/mobile network basic connectivity.",
        "- [ ] Touchscreen/audio/camera basic functionality.",
        "- [ ] Charging + thermal behavior appears normal.",
        "",
        "## Stability",
        "- [ ] 15-30 min idle: no panic/reboot.",
        "- [ ] 10-15 min light load: no abnormal throttling/reboot.",
        "",
        "## Report Back",
        "- [ ] Export dmesg/logcat snippets if anomaly appears.",
        "- [ ] Provide pass/fail + failing step index for next patch round.",
        "",
    ])

    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
