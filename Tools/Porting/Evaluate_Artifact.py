#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("artifacts/umi_bundle/pack-info.txt")
out = Path("artifacts/flash-readiness.txt")

if not p.exists():
    out.write_text("status=unknown\nreason=pack-info-missing\n", encoding="utf-8")
    print("pack-info missing")
    raise SystemExit(0)

kv = {}
for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        kv[k.strip()] = v.strip()

cnt = int(re.sub(r"\D", "", kv.get("umi_bundle_xiaomi_dtb_count", "0")) or 0)
hint = kv.get("flash_ready_hint", "no")

status = "not_ready"
reason = "insufficient-xiaomi-dtb"
if cnt >= 1 and hint == "candidate":
    status = "candidate"
    reason = "structure-ok-need-runtime-test"

out.write_text(f"status={status}\nreason={reason}\n", encoding="utf-8")
print(f"wrote {out}: {status}")
