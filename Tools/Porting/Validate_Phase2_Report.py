#!/usr/bin/env python3
from pathlib import Path

from Phase2_Decision import ALLOWED_NEXT_ACTION

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
    "bootimg_status",
    "bootimg_required_bytes",
    "bootimg_required_bytes_parse",
]

ALLOWED_YES_NO = {"yes", "no"}
ALLOWED_PARSE = {"exact", "default-empty", "default-invalid", "unknown"}


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
    invalid = []

    next_action = rep.get("next_action", "")
    if next_action and next_action not in ALLOWED_NEXT_ACTION:
        invalid.append(f"next_action:{next_action}")

    runtime_ready = rep.get("runtime_ready", "")
    if runtime_ready and runtime_ready not in ALLOWED_YES_NO:
        invalid.append(f"runtime_ready:{runtime_ready}")

    parse_state = rep.get("bootimg_required_bytes_parse", "")
    if parse_state and parse_state not in ALLOWED_PARSE:
        invalid.append(f"bootimg_required_bytes_parse:{parse_state}")

    required_bytes = rep.get("bootimg_required_bytes", "")
    if required_bytes and not required_bytes.lstrip("-").isdigit():
        invalid.append(f"bootimg_required_bytes:{required_bytes}")

    status = "ok" if not missing and not invalid else "invalid"

    OUT.write_text(
        "\n".join([
            f"status={status}",
            f"required_keys={len(REQ_KEYS)}",
            f"missing_keys={','.join(missing)}",
            f"invalid_values={','.join(invalid)}",
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
