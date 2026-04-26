#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ART = Path("artifacts")
OUT = ART / "driver-integration-manifest.txt"

DEFAULT_PENDING = [
    "display_pipeline",
    "audio_stack",
    "camera_sensor_module",
    "camera_isp_path",
    "thermal_power_tuning",
]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    if OUT.exists() and OUT.read_text(encoding="utf-8", errors="ignore").strip():
        print(f"keep existing {OUT}")
        return 0

    lines = [
        "# Driver integration manifest",
        "# Mark completed work with: integrated:<item>",
        "# Keep unfinished work as: pending:<item>",
        "# This file is consumed by Build_Driver_Integration_Status.py",
        "",
    ]
    lines.extend([f"pending:{item}" for item in DEFAULT_PENDING])

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
