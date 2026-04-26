#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

from PortConfig import get_supported_devices, load_port_config


def main() -> int:
    device = (os.getenv("DEVICE") or (sys.argv[1] if len(sys.argv) > 1 else "")).strip()
    supported = get_supported_devices(load_port_config())
    if not device:
        print("missing-device")
        return 1
    if supported and device not in supported:
        print(f"unsupported-device:{device}")
        print("supported=" + ",".join(supported))
        return 2
    print(device)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
