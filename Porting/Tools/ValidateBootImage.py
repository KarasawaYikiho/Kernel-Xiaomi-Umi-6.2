#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import re
import struct

ANDROID_MAGIC = b"ANDROID!"
ZIP_MAGICS = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")

ART = Path("artifacts")
OUT = ART / "bootimg-info.txt"
ROM_ANALYSIS = Path("Porting/OfficialRomAnalysis.md")
ROM_BASELINE_ENV = Path("Porting/OfficialRomBaseline/BootImageBaseline.env")
BOOT_BUILD = ART / "bootimg-build.txt"
OFFICIAL_ROM_BASELINE = ART / "official-rom-baseline.json"
DEFAULT_REQUIRED_BYTES = 134217728  # 128 MiB


def write_kv(lines: list[str]) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_required_bytes(raw: str | None) -> tuple[int, str]:
    """
    Parse BOOTIMG_REQUIRED_BYTES safely.
    Returns (required_bytes, parse_note).

    parse_note values:
      - exact: valid integer parsed from env
      - default-empty: env missing/empty, fell back to default
      - default-invalid: env invalid, fell back to default
    """
    if raw is None or not str(raw).strip():
        return DEFAULT_REQUIRED_BYTES, "default-empty"

    try:
        return int(str(raw).strip()), "exact"
    except (TypeError, ValueError):
        return DEFAULT_REQUIRED_BYTES, "default-invalid"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_prefix(path: Path, n: int = 8) -> bytes:
    with path.open("rb") as f:
        return f.read(n)


def _detect_format(path: Path) -> tuple[str, str]:
    prefix = _read_prefix(path, 8)
    if prefix.startswith(ANDROID_MAGIC):
        return "android_bootimg", prefix.hex()
    if any(prefix.startswith(m) for m in ZIP_MAGICS):
        return "zip", prefix[:4].hex()
    if not prefix:
        return "empty", ""
    return "unknown", prefix.hex()


def _load_rom_boot_reference() -> tuple[str, str]:
    if not ROM_ANALYSIS.exists():
        return "", ""
    text = ROM_ANALYSIS.read_text(encoding="utf-8", errors="ignore")
    m = re.search(
        r"`boot\.img`: size=`(\d+)` sha256=`([0-9a-f]{64})`", text, re.IGNORECASE
    )
    if not m:
        return "", ""
    return m.group(1), m.group(2).lower()


def _load_env_kv(path: Path) -> dict[str, str]:
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


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def _parse_header_version(path: Path) -> str:
    try:
        with path.open("rb") as f:
            data = f.read(44)
        if len(data) < 44 or data[:8] != ANDROID_MAGIC:
            return ""
        return str(struct.unpack("<I", data[40:44])[0])
    except Exception:
        return ""


def main() -> int:
    required_bytes, parse_note = parse_required_bytes(
        os.getenv("BOOTIMG_REQUIRED_BYTES")
    )
    rom_expected_size, rom_expected_sha = _load_rom_boot_reference()
    baseline_env = _load_env_kv(ROM_BASELINE_ENV)
    baseline_json = _load_json(OFFICIAL_ROM_BASELINE)
    boot_build = _load_env_kv(BOOT_BUILD)
    expected_header_version = baseline_env.get("BOOTIMG_HEADER_VERSION", "")
    baseline_path = baseline_env.get("ROM_BOOTIMG_PATH", "")
    official_bootimg_path = os.getenv("OFFICIAL_BOOTIMG_PATH", "").strip()
    baseline_source_file = str(baseline_json.get("source_file", "") or "")
    source = boot_build.get("source", "")
    source_ref = boot_build.get("source_ref", "")
    strict_official_reference = os.getenv(
        "BOOTIMG_STRICT_OFFICIAL_REFERENCE", "yes"
    ).strip().lower() in {"1", "true", "yes", "on"}

    bootimg = ART / "boot.img"
    if not bootimg.exists():
        write_kv(
            [
                "status=missing",
                "reason=bootimg-not-found",
                "path=",
                "size_bytes=0",
                "sha256=",
                f"required_bytes={required_bytes}",
                f"required_bytes_parse={parse_note}",
                f"rom_expected_size_bytes={rom_expected_size}",
                f"rom_expected_sha256={rom_expected_sha}",
                f"rom_expected_header_version={expected_header_version}",
                f"bootimg_build_source={source}",
                f"bootimg_build_source_ref={source_ref}",
                f"official_bootimg_path={official_bootimg_path}",
                f"baseline_bootimg_path={baseline_path}",
                f"official_reference_present={'yes' if (rom_expected_size or rom_expected_sha or expected_header_version or official_bootimg_path or baseline_path or baseline_source_file) else 'no'}",
                "rom_size_match=unknown",
                "rom_sha256_match=unknown",
                "rom_header_version_match=unknown",
                "official_reference_gate=no",
                "official_reference_gate_reasons=bootimg-not-found",
                "size_match=no",
                "flash_ready=no",
            ]
        )
        print(f"wrote {OUT}: missing")
        return 0

    size = bootimg.stat().st_size
    sha = _sha256(bootimg)
    detected_format, header_magic = _detect_format(bootimg)
    actual_header_version = _parse_header_version(bootimg)
    rom_size_match = "unknown"
    rom_sha_match = "unknown"
    rom_header_match = "unknown"
    if rom_expected_size:
        rom_size_match = "yes" if str(size) == rom_expected_size else "no"
    if rom_expected_sha:
        rom_sha_match = "yes" if sha == rom_expected_sha else "no"
    if expected_header_version:
        rom_header_match = (
            "yes" if actual_header_version == expected_header_version else "no"
        )

    official_reference_present = (
        "yes"
        if (
            rom_expected_size
            or rom_expected_sha
            or expected_header_version
            or official_bootimg_path
            or baseline_path
            or baseline_source_file
        )
        else "no"
    )
    official_reference_gate = "yes"
    gate_reasons: list[str] = []
    if strict_official_reference and official_reference_present != "yes":
        official_reference_gate = "no"
        gate_reasons.append("official_reference_missing")
    if strict_official_reference and not source:
        official_reference_gate = "no"
        gate_reasons.append("boot_build_source_missing")
    elif source and source not in {
        "official_rom_baseline",
        "official_rom_repacked_kernel",
        "prebuilt_path",
        "mkbootimg",
    }:
        official_reference_gate = "no"
        gate_reasons.append(f"boot_build_source_untrusted:{source}")
    if (
        detected_format == "android_bootimg"
        and expected_header_version
        and rom_header_match != "yes"
    ):
        official_reference_gate = "no"
        gate_reasons.append("header_version_mismatch")
    if (
        detected_format == "android_bootimg"
        and rom_expected_size
        and rom_size_match != "yes"
    ):
        official_reference_gate = "no"
        gate_reasons.append("size_mismatch_vs_official")

    # BOOTIMG_REQUIRED_BYTES is treated as the final target size.
    if detected_format != "android_bootimg":
        size_match = "yes" if (required_bytes <= 0 or size == required_bytes) else "no"
        status = "invalid_format"
        if detected_format == "zip":
            reason = "bootimg-is-zip-not-android-image"
        elif detected_format == "empty":
            reason = "bootimg-empty"
        else:
            reason = "bootimg-header-unrecognized"
    elif required_bytes <= 0:
        size_match = "yes"
        status = "ok"
        reason = "size-check-disabled"
    else:
        size_match = "yes" if size == required_bytes else "no"
        status = "ok" if size_match == "yes" else "size_mismatch"
        reason = "release-ready-size-ok" if size_match == "yes" else "size-not-target"

    if status == "ok" and official_reference_gate != "yes":
        status = "reference_mismatch"
        reason = gate_reasons[0] if gate_reasons else "official-reference-gate-failed"

    write_kv(
        [
            f"status={status}",
            f"reason={reason}",
            f"path={bootimg.as_posix()}",
            f"size_bytes={size}",
            f"sha256={sha}",
            f"required_bytes={required_bytes}",
            f"required_bytes_parse={parse_note}",
            f"format={detected_format}",
            f"header_magic={header_magic}",
            f"header_version={actual_header_version}",
            f"size_match={size_match}",
            f"rom_expected_size_bytes={rom_expected_size}",
            f"rom_expected_sha256={rom_expected_sha}",
            f"rom_expected_header_version={expected_header_version}",
            f"rom_size_match={rom_size_match}",
            f"rom_sha256_match={rom_sha_match}",
            f"rom_header_version_match={rom_header_match}",
            f"bootimg_build_source={source}",
            f"bootimg_build_source_ref={source_ref}",
            f"official_bootimg_path={official_bootimg_path}",
            f"baseline_bootimg_path={baseline_path}",
            f"official_reference_present={official_reference_present}",
            f"official_reference_gate={official_reference_gate}",
            "official_reference_gate_reasons=" + ",".join(gate_reasons),
            f"flash_ready={'yes' if status == 'ok' and size_match == 'yes' and official_reference_gate == 'yes' else 'no'}",
        ]
    )
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
