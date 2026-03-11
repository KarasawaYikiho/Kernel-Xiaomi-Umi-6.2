#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "artifact-completeness.txt"

REQUIRED = [
    "phase2-report.txt",
    "run-meta.txt",
    "flash-readiness.txt",
    "dtb-postcheck.txt",
    "anykernel-info.txt",
]

OPTIONAL = [
    "dtb-miss-analysis.txt",
    "phase2-umi-focused-package.zip",
    "AnyKernel3-umi-candidate.zip",
    "anykernel-validate.txt",
    "bootimg-info.txt",
    "bootimg-build.txt",
    "action-validation-checklist.md",
]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    missing_required = [p for p in REQUIRED if not (ART / p).exists()]
    present_required = [p for p in REQUIRED if (ART / p).exists()]
    present_optional = [p for p in OPTIONAL if (ART / p).exists()]

    status = "ok" if not missing_required else "incomplete"

    lines = [
        f"status={status}",
        f"required_total={len(REQUIRED)}",
        f"required_present={len(present_required)}",
        f"required_missing={len(missing_required)}",
        "missing_required=" + ",".join(missing_required),
        "present_optional=" + ",".join(present_optional),
    ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
