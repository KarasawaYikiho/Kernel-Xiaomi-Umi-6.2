#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "phase2-report-validate.txt"
REQ_KEYS = [
    "phase2_report",
    "device",
    "defconfig_rc",
    "build_rc",
    "flash_status",
    "anykernel_ok",
    "anykernel_validate_status",
    "manifest_hit_ratio",
    "next_action",
    "runtime_ready",
]


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
    rep = parse_kv(ART / "phase2-report.txt")
    missing = [k for k in REQ_KEYS if k not in rep or rep.get(k, "") == ""]
    status = "ok" if not missing else "invalid"

    OUT.write_text(
        "\n".join([
            f"status={status}",
            f"required_keys={len(REQ_KEYS)}",
            f"missing_keys={','.join(missing)}",
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
