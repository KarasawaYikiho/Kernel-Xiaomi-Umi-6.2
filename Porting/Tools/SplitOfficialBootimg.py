#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PortConfig import get_nested, load_port_config

DEFAULT_PARTS_DIR = Path("Porting/OfficialRomBaseline/BootImgParts")
DEFAULT_MANIFEST = Path("Porting/OfficialRomBaseline/Manifest.json")
DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024


def default_input_path() -> Path:
    config = load_port_config()
    explicit = get_nested(config, "official_rom", "default_bootimg").strip()
    if explicit:
        return Path(explicit)
    default_dir = get_nested(config, "official_rom", "default_dir").strip()
    return Path(default_dir) / "boot.img" if default_dir else Path("boot.img")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(path: Path, manifest: dict) -> None:
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def split_bootimg(
    input_path: Path, parts_dir: Path, chunk_size: int
) -> tuple[int, int]:
    parts_dir.mkdir(parents=True, exist_ok=True)
    for existing in parts_dir.glob("boot.img.part*"):
        existing.unlink()
    for existing in parts_dir.glob("BootImgPart*.bin"):
        existing.unlink()

    count = 0
    with input_path.open("rb") as src:
        while True:
            data = src.read(chunk_size)
            if not data:
                break
            (parts_dir / f"BootImgPart{count:04d}.bin").write_bytes(data)
            count += 1
    return count, input_path.stat().st_size


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(default_input_path()))
    parser.add_argument("--parts-dir", default=str(DEFAULT_PARTS_DIR))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    args = parser.parse_args()

    input_path = Path(args.input)
    parts_dir = Path(args.parts_dir)
    manifest_path = Path(args.manifest)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    part_count, size = split_bootimg(input_path, parts_dir, args.chunk_size)
    sha256 = sha256_file(input_path)

    manifest = load_manifest(manifest_path)
    manifest.setdefault("bootimg", {})
    manifest["bootimg"]["required_bytes"] = size
    manifest["bootimg"]["sha256"] = sha256
    manifest["bootimg"]["parts"] = {
        "dir": parts_dir.as_posix(),
        "chunk_size": args.chunk_size,
        "count": part_count,
        "filename_prefix": "BootImgPart",
    }
    write_manifest(manifest_path, manifest)

    print(f"split_source={input_path}")
    print(f"parts_dir={parts_dir.as_posix()}")
    print(f"part_count={part_count}")
    print(f"chunk_size={args.chunk_size}")
    print(f"sha256={sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
