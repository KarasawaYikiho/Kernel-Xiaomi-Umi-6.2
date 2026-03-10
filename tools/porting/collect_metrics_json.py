#!/usr/bin/env python3
from pathlib import Path
import json

ART = Path("artifacts")
OUT = ART / "phase2-metrics.json"


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
    valid = parse_kv(ART / "phase2-report-validate.txt")

    obj = {
        "run": {
            "id": meta.get("run_id", ""),
            "number": meta.get("run_number", ""),
            "sha": meta.get("sha", ""),
            "device": meta.get("device", report.get("device", "unknown")),
        },
        "build": {
            "defconfig_rc": report.get("defconfig_rc", "n/a"),
            "build_rc": report.get("build_rc", "n/a"),
        },
        "dtb": {
            "hit_ratio": report.get("manifest_hit_ratio", "0.000"),
            "miss_bucket_total": report.get("miss_bucket_total", "0"),
        },
        "packaging": {
            "flash_status": report.get("flash_status", "unknown"),
            "anykernel_ok": report.get("anykernel_ok", "no"),
            "anykernel_validate_status": report.get("anykernel_validate_status", "unknown"),
            "anykernel_validate_reason": report.get("anykernel_validate_reason", "n/a"),
        },
        "report": {
            "next_action": report.get("next_action", "collect-more-data"),
            "schema_status": valid.get("status", "unknown"),
        },
    }

    OUT.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
