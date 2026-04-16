#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "artifact-completeness.txt"

REQUIRED = [
    "phase2-report.txt",
    "run-meta.txt",
    "flash-readiness.txt",
]

PHASE2_REQUIRED = [
    "dtb-postcheck.txt",
    "anykernel-info.txt",
]

OPTIONAL = [
    "dtb-miss-analysis.txt",
    "phase2-device-package.zip",
    "AnyKernel3-candidate.zip",
    "anykernel-validate.txt",
    "bootimg-info.txt",
    "bootimg-build.txt",
    "driver-integration-status.txt",
    "plan-progress.txt",
    "plan-progress.md",
    "decision-consistency.txt",
    "postprocess-status.txt",
    "action-validation-checklist.md",
    "runtime-validation-input.md",
    "runtime-validation-result.txt",
    "runtime-validation-summary.md",
]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    missing_required = [p for p in REQUIRED if not (ART / p).exists()]
    present_required = [p for p in REQUIRED if (ART / p).exists()]
    missing_phase2 = [p for p in PHASE2_REQUIRED if not (ART / p).exists()]
    present_phase2 = [p for p in PHASE2_REQUIRED if (ART / p).exists()]
    present_optional = [p for p in OPTIONAL if (ART / p).exists()]

    build_context_present = any(
        (ART / p).exists()
        for p in [
            "build-exit.txt",
            "make-build.log",
            "make-defconfig.log",
            "make-target-dtbs.log",
            "summary.txt",
        ]
    )

    if missing_required:
        status = "incomplete"
    elif not build_context_present:
        status = "partial"
    elif build_context_present and missing_phase2:
        status = "incomplete"
    else:
        status = "ok"

    lines = [
        f"status={status}",
        f"required_total={len(REQUIRED)}",
        f"required_present={len(present_required)}",
        f"required_missing={len(missing_required)}",
        f"phase2_required_total={len(PHASE2_REQUIRED)}",
        f"phase2_required_present={len(present_phase2)}",
        f"phase2_required_missing={len(missing_phase2)}",
        f"build_context_present={'yes' if build_context_present else 'no'}",
        "missing_required=" + ",".join(missing_required),
        "missing_phase2_required=" + ",".join(missing_phase2),
        "present_optional=" + ",".join(present_optional),
    ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
