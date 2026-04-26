#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

ART = Path("artifacts")
BASELINE_DIR = Path("Porting/OfficialRomBaseline")
MANIFEST_PATH = BASELINE_DIR / "Manifest.json"
ENV_PATH = BASELINE_DIR / "BootImageBaseline.env"
DEFAULT_PARTS_DIR = BASELINE_DIR / "BootImgParts"
DEFAULT_OUTPUT = ART / "official-rom-baseline-boot.img"


def load_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_path(raw: str) -> Path | None:
    value = (raw or "").strip()
    if not value:
        return None
    return Path(value)


def locate_parts_dir(env_kv: dict[str, str], manifest: dict) -> Path:
    part_meta = (
        manifest.get("bootimg", {}).get("parts", {})
        if isinstance(manifest, dict)
        else {}
    )
    return (
        normalize_path(env_kv.get("ROM_BOOTIMG_PARTS_DIR", ""))
        or normalize_path(str(part_meta.get("dir", "")))
        or DEFAULT_PARTS_DIR
    )


def locate_boot_path(env_kv: dict[str, str]) -> Path | None:
    explicit = normalize_path(os.getenv("OFFICIAL_BOOTIMG_PATH", ""))
    if explicit and explicit.exists():
        return explicit
    baseline = normalize_path(env_kv.get("ROM_BOOTIMG_PATH", ""))
    if baseline and baseline.exists():
        return baseline
    return None


def list_part_files(parts_dir: Path, manifest: dict) -> list[Path]:
    part_meta = (
        manifest.get("bootimg", {}).get("parts", {})
        if isinstance(manifest, dict)
        else {}
    )
    prefix = str(part_meta.get("filename_prefix", "")).strip()
    count = part_meta.get("count")
    duplicate_parts = part_meta.get("duplicate_parts", {})
    if prefix and isinstance(count, int) and count > 0:
        parts = []
        for idx in range(count):
            name = f"{prefix}{idx:04d}.bin"
            if isinstance(duplicate_parts, dict):
                name = str(duplicate_parts.get(name, name))
            parts.append(parts_dir / name)
        return parts
    parts = [p for p in parts_dir.iterdir() if p.is_file()]
    if prefix:
        parts = [p for p in parts if p.name.startswith(prefix)]
    return sorted(parts)


def materialize_from_parts(
    parts_dir: Path, out_path: Path, manifest: dict
) -> tuple[Path | None, str]:
    if not parts_dir.exists() or not parts_dir.is_dir():
        return None, f"parts-dir-missing:{parts_dir}"
    parts = list_part_files(parts_dir, manifest)
    if not parts:
        return None, f"parts-missing:{parts_dir}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as out:
        for part in parts:
            if not part.exists():
                return None, f"part-missing:{part}"
            out.write(part.read_bytes())
    return out_path, "ok"


def main() -> int:
    env_kv = load_env(ENV_PATH)
    manifest = load_manifest(MANIFEST_PATH)
    expected_sha = env_kv.get("ROM_BOOTIMG_SHA256", "") or str(
        manifest.get("bootimg", {}).get("sha256", "")
    )
    expected_size = str(
        env_kv.get("BOOTIMG_REQUIRED_BYTES", "")
        or manifest.get("bootimg", {}).get("required_bytes", "")
    )

    existing = locate_boot_path(env_kv)
    if existing:
        print(existing)
        return 0

    parts_dir = locate_parts_dir(env_kv, manifest)
    out_path = DEFAULT_OUTPUT
    materialized, reason = materialize_from_parts(parts_dir, out_path, manifest)
    if not materialized:
        print(reason)
        return 1

    actual_sha = sha256_file(materialized)
    if expected_sha and actual_sha != expected_sha:
        print(f"sha256-mismatch:{actual_sha}")
        return 2
    if (
        expected_size
        and expected_size.isdigit()
        and materialized.stat().st_size != int(expected_size)
    ):
        print(f"size-mismatch:{materialized.stat().st_size}")
        return 3

    print(materialized.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
