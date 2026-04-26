#!/usr/bin/env python3
from pathlib import Path
import re

ART = Path("artifacts")
OUT = ART / "build-error-summary.txt"
LOGS = [
    ART / "make-defconfig.log",
    ART / "make-build.log",
    ART / "make-target-dtbs.log",
    ART / "make-dtb-manifest.log",
]

ERR_PAT = re.compile(r"(error:|undefined reference|No rule to make target|fatal error:)", re.I)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    findings: list[str] = []

    for log in LOGS:
      if not log.exists():
            continue
      lines = log.read_text(encoding="utf-8", errors="ignore").splitlines()
      for i, line in enumerate(lines):
            if ERR_PAT.search(line):
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                chunk = " | ".join(x.strip() for x in lines[start:end] if x.strip())
                findings.append(f"{log.name}:{i+1}: {chunk}")

    # dedupe keep order
    seen = set()
    uniq = []
    for f in findings:
        if f not in seen:
            seen.add(f)
            uniq.append(f)

    OUT.write_text(
        "\n".join([
            f"error_hits={len(uniq)}",
            "samples=" + (" || ".join(uniq[:20]) if uniq else ""),
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {len(uniq)} hits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
