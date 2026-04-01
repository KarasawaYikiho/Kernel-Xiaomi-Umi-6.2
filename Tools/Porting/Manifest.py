#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def normalize_item(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def parse_driver_manifest(
    path: Path,
) -> tuple[list[str], set[str], set[str], set[str]]:
    comments: list[str] = []
    integrated: set[str] = set()
    pending: set[str] = set()
    unknown: set[str] = set()

    if not path.exists():
        return comments, integrated, pending, unknown

    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line:
            comments.append("")
            continue
        if line.startswith("#"):
            comments.append(line)
            continue
        if line.startswith("integrated:"):
            item = normalize_item(line.split(":", 1)[1])
            if item:
                integrated.add(item)
            continue
        if line.startswith("pending:"):
            item = normalize_item(line.split(":", 1)[1])
            if item:
                pending.add(item)
            continue
        unknown.add(line)

    return comments, integrated, pending, unknown
