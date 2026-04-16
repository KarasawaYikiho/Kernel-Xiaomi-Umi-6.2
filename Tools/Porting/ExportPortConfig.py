#!/usr/bin/env python3
from __future__ import annotations

from PortConfig import get_nested, get_supported_devices, load_port_config


def main() -> int:
    config = load_port_config()
    lines = [
        f"PORT_NAME={get_nested(config, 'port_name')}",
        f"PORT_WORKFLOW_NAME={get_nested(config, 'workflow_name')}",
        f"REFERENCE_BASELINE_DEVICE={get_nested(config, 'reference_baseline_device')}",
        f"SOURCE_REPO={get_nested(config, 'source', 'repo')}",
        f"SOURCE_BRANCH={get_nested(config, 'source', 'branch')}",
        f"TARGET_REPO={get_nested(config, 'target', 'repo')}",
        f"TARGET_BRANCH={get_nested(config, 'target', 'branch')}",
        f"TOOLCHAIN_NAME={get_nested(config, 'toolchain', 'name')}",
        f"TOOLCHAIN_URL={get_nested(config, 'toolchain', 'url')}",
        f"TOOLCHAIN_ARCHIVE={get_nested(config, 'toolchain', 'archive')}",
        f"TOOLCHAIN_INSTALL_DIR={get_nested(config, 'toolchain', 'install_dir')}",
        f"OFFICIAL_BOOTIMG_DEFAULT={get_nested(config, 'official_rom', 'default_bootimg')}",
        f"OFFICIAL_ROM_DIR_DEFAULT={get_nested(config, 'official_rom', 'default_dir')}",
        f"OFFICIAL_ROM_ZIP_DEFAULT={get_nested(config, 'official_rom', 'default_zip')}",
        f"OFFICIAL_ROM_BASELINE_DIR={get_nested(config, 'official_rom', 'baseline_dir')}",
        f"OFFICIAL_ROM_MANIFEST={get_nested(config, 'official_rom', 'manifest')}",
        f"OFFICIAL_ROM_ENV={get_nested(config, 'official_rom', 'env')}",
        "SUPPORTED_DEVICES=" + ",".join(get_supported_devices(config)),
    ]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
