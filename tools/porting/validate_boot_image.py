#!/usr/bin/env python3
from pathlib import Path
import os

ART = Path("artifacts")
OUT = ART / "bootimg-info.txt"


def write_kv(lines: list[str]) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    required_bytes = int(os.getenv("BOOTIMG_REQUIRED_BYTES", "268435456"))  # 256 MiB

    bootimg = ART / "boot.img"
    if not bootimg.exists():
        write_kv([
            "status=missing",
            "reason=bootimg-not-found",
            "path=",
            "size_bytes=0",
            f"required_bytes={required_bytes}",
            "size_match=no",
            "flash_ready=no",
        ])
        print(f"wrote {OUT}: missing")
        return 0

    size = bootimg.stat().st_size
    size_match = "yes" if size == required_bytes else "no"
    status = "ok" if size_match == "yes" else "size_mismatch"
    reason = "release-ready-size-ok" if size_match == "yes" else "size-not-256MiB"

    write_kv([
        f"status={status}",
        f"reason={reason}",
        f"path={bootimg.as_posix()}",
        f"size_bytes={size}",
        f"required_bytes={required_bytes}",
        f"size_match={size_match}",
        f"flash_ready={'yes' if size_match == 'yes' else 'no'}",
    ])
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
