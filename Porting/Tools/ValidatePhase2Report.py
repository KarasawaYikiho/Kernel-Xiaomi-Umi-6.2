#!/usr/bin/env python3
from pathlib import Path

from KvUtils import parse_kv
from Phase2Decision import ALLOWED_NEXT_ACTION, DEFAULT_BOOTIMG_REQUIRED_BYTES_STR

ART = Path("artifacts")
OUT = ART / "phase2-report-validate.txt"
REQ_KEYS = [
    "phase2_report",
    "device",
    "defconfig_rc",
    "build_rc",
    "dtbs_rc",
    "phase2_build_gate",
    "phase2_dtbs_gate",
    "phase2_rom_gate",
    "phase2_complete",
    "flash_status",
    "anykernel_ok",
    "anykernel_validate_status",
    "manifest_hit_ratio",
    "next_action",
    "runtime_ready",
    "bootimg_status",
    "bootimg_required_bytes",
    "bootimg_required_bytes_parse",
    "driver_integration_status",
]

ALLOWED_YES_NO = {"yes", "no"}
ALLOWED_PARSE = {"exact", "default-empty", "default-invalid", "unknown"}
ALLOWED_DRIVER_INTEGRATION = {"pending", "partial", "complete", "unknown"}
ALLOWED_GATE = {"pass", "fail"}


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

    required_bytes = rep.get(
        "bootimg_required_bytes", DEFAULT_BOOTIMG_REQUIRED_BYTES_STR
    )
    if required_bytes and not required_bytes.lstrip("-").isdigit():
        invalid.append(f"bootimg_required_bytes:{required_bytes}")

    driver_integration = rep.get("driver_integration_status", "")
    if driver_integration and driver_integration not in ALLOWED_DRIVER_INTEGRATION:
        invalid.append(f"driver_integration_status:{driver_integration}")

    for gate_key in ("phase2_build_gate", "phase2_dtbs_gate", "phase2_rom_gate"):
        gate = rep.get(gate_key, "")
        if gate and gate not in ALLOWED_GATE:
            invalid.append(f"{gate_key}:{gate}")

    if rep.get("dtbs_rc") != "0":
        invalid.append(f"dtbs_rc:{rep.get('dtbs_rc', '')}")
    if rep.get("phase2_complete") != "yes":
        invalid.append(f"phase2_complete:{rep.get('phase2_complete', '')}")
    if rep.get("runtime_ready") == "yes" and rep.get("phase2_complete") != "yes":
        invalid.append("runtime_ready_without_phase2_complete")

    status = "ok" if not missing and not invalid else "invalid"

    OUT.write_text(
        "\n".join(
            [
                f"status={status}",
                f"required_keys={len(REQ_KEYS)}",
                f"missing_keys={','.join(missing)}",
                f"invalid_values={','.join(invalid)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {status}")
    return 0 if status == "ok" else 2


if __name__ == "__main__":
    raise SystemExit(main())
