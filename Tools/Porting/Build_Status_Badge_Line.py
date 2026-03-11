#!/usr/bin/env python3
from pathlib import Path

from Kv_Utils import parse_kv
from Phase2_Decision import derive_runtime_ready

ART = Path("artifacts")
OUT = ART / "status-badge-line.txt"



def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    r = parse_kv(ART / "phase2-report.txt")

    build_rc = r.get("build_rc", "n/a")
    flash = r.get("flash_status", "unknown")
    anyk = r.get("anykernel_ok", "no")
    anyk_val = r.get("anykernel_validate_status", "unknown")
    ratio = r.get("manifest_hit_ratio", "0.000")
    next_action = r.get("next_action", "collect-more-data")
    runtime_ready = r.get("runtime_ready", "no")
    driver_integration = r.get("driver_integration_status", "pending")

    expected_runtime_ready = derive_runtime_ready(next_action)
    runtime_marker = "ok" if runtime_ready == expected_runtime_ready else f"mismatch(expected:{expected_runtime_ready})"

    line = (
        f"build={build_rc} | flash={flash} | anykernel={anyk}/{anyk_val} "
        f"| driver_integration={driver_integration} "
        f"| runtime_ready={runtime_ready}({runtime_marker}) | hit_ratio={ratio} | next={next_action}"
    )
    OUT.write_text(line + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
