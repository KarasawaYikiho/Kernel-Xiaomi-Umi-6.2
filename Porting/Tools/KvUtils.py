#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def parse_kv(path: Path) -> dict[str, str]:
    kv: dict[str, str] = {}
    if not path.exists():
        return kv
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip().lstrip("\ufeff")
            kv[key] = value.strip()
    return kv


def split_csv(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]
