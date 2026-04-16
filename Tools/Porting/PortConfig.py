#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path("Porting/Sm8250PortConfig.json")


def load_port_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def get_nested(config: dict, *keys: str, default: str = "") -> str:
    cur: object = config
    for key in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key, default)
    return str(cur if cur is not None else default)


def get_supported_devices(config: dict) -> list[str]:
    value = config.get("supported_devices", []) if isinstance(config, dict) else []
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
