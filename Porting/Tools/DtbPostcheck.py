#!/usr/bin/env python3
from pathlib import Path

all_paths = Path("artifacts/all_dtb_paths.txt")
manifest = Path("artifacts/target_dtb_manifest.txt")
out = Path("artifacts/dtb-postcheck.txt")

def norm_path(s: str) -> str:
    return s.replace('\\', '/').strip()


all_set = set()
if all_paths.exists():
    all_set = {norm_path(x) for x in all_paths.read_text(encoding='utf-8', errors='ignore').splitlines() if x.strip()}

wanted = []
if manifest.exists():
    wanted = [x.strip() for x in manifest.read_text(encoding='utf-8', errors='ignore').splitlines() if x.strip()]

all_basenames = {p.rsplit('/', 1)[-1] for p in all_set}

hit = []
miss = []
for name in wanted:
    found = (name in all_basenames) or any(p.endswith('/' + name) for p in all_set)
    (hit if found else miss).append(name)

wanted_n = len(wanted)
hit_n = len(hit)
miss_n = len(miss)
hit_ratio = (hit_n / wanted_n) if wanted_n else 0.0

out.write_text(
    "\n".join([
        f"wanted={wanted_n}",
        f"hit={hit_n}",
        f"miss={miss_n}",
        f"hit_ratio={hit_ratio:.3f}",
        "hit_names=" + (",".join(hit) if hit else ""),
        "miss_names=" + (",".join(miss) if miss else ""),
    ]) + "\n",
    encoding='utf-8'
)
print(f"wrote {out} (hit_ratio={hit_ratio:.3f})")
