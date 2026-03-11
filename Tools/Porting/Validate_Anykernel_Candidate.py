#!/usr/bin/env python3
from pathlib import Path
import zipfile

ART = Path("artifacts")
ZIP_PATH = ART / "AnyKernel3-umi-candidate.zip"
OUT = ART / "anykernel-validate.txt"

REQUIRED_ENTRIES = [
    "anykernel.sh",
    "Image.gz",
]


def write(lines: list[str]) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not ZIP_PATH.exists():
        write([
            "status=missing",
            "reason=candidate-zip-not-found",
            "has_anykernel_sh=no",
            "has_imagegz=no",
            "has_dtb=no",
            "entry_count=0",
            "missing_required=anykernel.sh,Image.gz",
        ])
        print(f"wrote {OUT}: missing")
        return 0

    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as zf:
            names = set(zf.namelist())
    except zipfile.BadZipFile:
        write([
            "status=invalid",
            "reason=bad-zip",
            "has_anykernel_sh=no",
            "has_imagegz=no",
            "has_dtb=no",
            "entry_count=0",
            "missing_required=anykernel.sh,Image.gz",
        ])
        print(f"wrote {OUT}: invalid")
        return 0

    missing = [e for e in REQUIRED_ENTRIES if e not in names]
    has_dtb = "yes" if "dtb" in names else "no"

    status = "ok" if not missing else "incomplete"
    reason = "structure-ok" if not missing else "missing-required-entries"

    write([
        f"status={status}",
        f"reason={reason}",
        f"has_anykernel_sh={'yes' if 'anykernel.sh' in names else 'no'}",
        f"has_imagegz={'yes' if 'Image.gz' in names else 'no'}",
        f"has_dtb={has_dtb}",
        f"entry_count={len(names)}",
        "missing_required=" + ",".join(missing),
    ])
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
