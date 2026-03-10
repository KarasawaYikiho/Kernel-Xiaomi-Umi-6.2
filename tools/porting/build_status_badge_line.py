#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "status-badge-line.txt"


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
    r = parse_kv(ART / "phase2-report.txt")

    build_rc = r.get("build_rc", "n/a")
    flash = r.get("flash_status", "unknown")
    anyk = r.get("anykernel_ok", "no")
    anyk_val = r.get("anykernel_validate_status", "unknown")
    ratio = r.get("manifest_hit_ratio", "0.000")
    next_action = r.get("next_action", "collect-more-data")

    line = f"build={build_rc} | flash={flash} | anykernel={anyk}/{anyk_val} | hit_ratio={ratio} | next={next_action}"
    OUT.write_text(line + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
