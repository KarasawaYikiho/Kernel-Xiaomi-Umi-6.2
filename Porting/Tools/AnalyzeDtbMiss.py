#!/usr/bin/env python3
from collections import Counter
from pathlib import Path

INP = Path("artifacts/dtb-postcheck.txt")
OUT = Path("artifacts/dtb-miss-analysis.txt")


def read_miss_names(path: Path) -> list[str]:
    if not path.exists():
        return []
    miss = ""
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("miss_names="):
            miss = line.split("=", 1)[1].strip()
            break
    if not miss:
        return []
    return [x.strip() for x in miss.split(",") if x.strip()]


def bucket(name: str) -> str:
    # e.g. sm8250-xiaomi-umi-foo.dtb -> sm8250-xiaomi-umi
    base = name[:-4] if name.endswith(".dtb") else name
    parts = base.split("-")
    if len(parts) >= 3:
        return "-".join(parts[:3])
    if len(parts) >= 2:
        return "-".join(parts[:2])
    return base


def main() -> int:
    misses = read_miss_names(INP)
    c = Counter(bucket(x) for x in misses)

    lines = [
        f"miss_total={len(misses)}",
        f"bucket_total={len(c)}",
        "top_buckets=" + ",".join(f"{k}:{v}" for k, v in c.most_common(20)),
        "miss_names=" + ",".join(misses[:50]),
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
