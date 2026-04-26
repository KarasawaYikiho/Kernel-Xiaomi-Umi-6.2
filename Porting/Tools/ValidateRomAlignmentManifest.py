#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from Manifest import parse_driver_manifest

ART = Path("artifacts")
MANIFEST = ART / "rom-alignment-manifest.txt"
OUT = ART / "rom-alignment-manifest-validate.txt"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    if not MANIFEST.exists():
        OUT.write_text("status=missing\nerrors=manifest_not_found\n", encoding="utf-8")
        print(f"wrote {OUT}: missing")
        return 0

    errors: list[str] = []
    _, integrated_items, pending_items, unknown = parse_driver_manifest(MANIFEST)

    for idx, raw in enumerate(
        MANIFEST.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1
    ):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("integrated:"):
            if not line.split(":", 1)[1].strip():
                errors.append(f"line_{idx}:empty_integrated_item")
            continue
        if line.startswith("pending:"):
            if not line.split(":", 1)[1].strip():
                errors.append(f"line_{idx}:empty_pending_item")
            continue
        if line.startswith("#"):
            continue
        errors.append(f"line_{idx}:invalid_prefix")

    if unknown:
        errors.extend([f"legacy:{item}" for item in sorted(unknown)])

    status = "ok" if not errors else "invalid"
    OUT.write_text(
        "\n".join(
            [
                f"status={status}",
                f"integrated_count={len(integrated_items)}",
                f"pending_count={len(pending_items)}",
                "errors=" + ",".join(errors),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
