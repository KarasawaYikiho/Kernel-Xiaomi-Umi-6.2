#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from KvUtils import parse_kv
from Manifest import parse_driver_manifest

ART = Path("artifacts")
MANIFEST = ART / "rom-alignment-manifest.txt"
OUT = ART / "rom-alignment-status.txt"
PHASE4_ITEMS = {"runtime_validation_official_rom"}


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    manifest_validate = parse_kv(ART / "rom-alignment-manifest-validate.txt")
    boot = parse_kv(ART / "bootimg-info.txt")
    dtb = parse_kv(ART / "dtb-postcheck.txt")
    evidence = parse_kv(ART / "driver-integration-evidence.txt")
    runtime_result = parse_kv(ART / "runtime-validation-result.txt")

    _, integrated, pending, _ = parse_driver_manifest(MANIFEST)

    manifest_validate_status = manifest_validate.get("status", "unknown")
    if manifest_validate_status not in ("ok", "unknown"):
        pending = set(pending)
        pending.add("manifest_format_invalid")

    if not boot:
        pending = set(pending)
        pending.add("bootimg_info_missing")
    if not dtb:
        pending = set(pending)
        pending.add("dtb_postcheck_missing")
    if not evidence:
        pending = set(pending)
        pending.add("rom_alignment_evidence_missing")
    if not runtime_result:
        pending = set(pending)
        pending.add("runtime_validation_result_missing")

    if integrated and not pending:
        status = "complete"
        reason = "rom_alignment_manifest_complete"
    elif integrated:
        status = "partial"
        reason = "rom_alignment_manifest_partial_with_followups"
    elif MANIFEST.exists():
        status = "pending"
        reason = "rom_alignment_backlog_initialized"
    else:
        status = "pending"
        reason = "rom_alignment_manifest_missing"

    phase2_pending = sorted(item for item in pending if item not in PHASE4_ITEMS)
    phase4_pending = sorted(item for item in pending if item in PHASE4_ITEMS)
    OUT.write_text(
        "\n".join(
            [
                f"status={status}",
                f"reason={reason}",
                f"integrated_count={len(integrated)}",
                f"manifest_validate_status={manifest_validate_status}",
                f"bootimg_status={boot.get('status', 'missing')}",
                f"bootimg_flash_ready={boot.get('flash_ready', 'no')}",
                f"dtb_hit_ratio={dtb.get('hit_ratio', '0.000')}",
                f"boot_chain_match={evidence.get('boot_chain_match', 'unknown')}",
                f"dtbo_match={evidence.get('dtbo_match', 'unknown')}",
                f"vbmeta_match={evidence.get('vbmeta_match', 'unknown')}",
                f"runtime_validation_overall={runtime_result.get('overall', 'UNKNOWN')}",
                "phase2_pending=" + ",".join(phase2_pending),
                "phase4_pending=" + ",".join(phase4_pending),
                "pending=" + ",".join(sorted(dict.fromkeys(pending))),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
