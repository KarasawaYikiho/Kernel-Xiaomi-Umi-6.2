#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ART = Path("artifacts")
OUT = ART / "rom-alignment-manifest.txt"

DEFAULT_PENDING = [
    "bootimg_release_packaging",
    "rom_boot_chain_consistency",
    "rom_dtbo_consistency",
    "rom_vbmeta_consistency",
    "rom_dynamic_partition_baseline",
    "dtb_target_coverage",
    "runtime_validation_official_rom",
]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    if OUT.exists() and OUT.read_text(encoding="utf-8", errors="ignore").strip():
        print(f"keep existing {OUT}")
        return 0

    lines = [
        "# ROM alignment manifest",
        "# Mark completed work with: integrated:<item>",
        "# Keep unfinished work as: pending:<item>",
        "# This file tracks release-chain alignment against the official ROM baseline.",
        "",
    ]
    lines.extend([f"pending:{item}" for item in DEFAULT_PENDING])

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
