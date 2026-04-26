#!/usr/bin/env python3
from pathlib import Path

from KvUtils import parse_kv
from Phase2Decision import derive_next_focus, parse_float

ART = Path("artifacts")
OUT = ART / "next-focus.txt"


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    report = parse_kv(ART / "phase2-report.txt")
    flash = report.get("flash_status", "unknown")
    anyk = report.get("anykernel_ok", "no")
    anyk_val = report.get("anykernel_validate_status", "unknown")
    hit_ratio = parse_float(report.get("manifest_hit_ratio", "0"), 0.0)
    build_rc = report.get("build_rc", "n/a")
    dtbs_rc = report.get("dtbs_rc", "n/a")
    report_next = report.get("next_action", "")
    runtime_overall = report.get("runtime_validation_overall", "UNKNOWN")
    runtime_failed_step = report.get("runtime_validation_failed_step", "")

    focus, reason = derive_next_focus(
        report_next_action=report_next,
        artifact_completeness=report.get("artifact_completeness", "unknown"),
        build_context_present=report.get("build_context_present", "unknown"),
        build_rc=build_rc,
        dtbs_rc=dtbs_rc,
        flash_status=flash,
        anykernel_ok=anyk,
        anykernel_validate_status=anyk_val,
        manifest_hit_ratio=hit_ratio,
        rom_alignment_status=report.get("rom_alignment_status", "pending"),
        rom_alignment_pending=report.get("rom_alignment_pending", ""),
        runtime_validation_overall=runtime_overall,
        runtime_validation_failed_step=runtime_failed_step,
    )

    OUT.write_text(
        "\n".join(
            [
                f"focus={focus}",
                f"reason={reason}",
                f"flash_status={flash}",
                f"anykernel_ok={anyk}",
                f"anykernel_validate_status={anyk_val}",
                f"manifest_hit_ratio={hit_ratio:.3f}",
                f"rom_alignment_status={report.get('rom_alignment_status', 'pending')}",
                f"rom_alignment_pending={report.get('rom_alignment_pending', '')}",
                f"build_rc={build_rc}",
                f"dtbs_rc={dtbs_rc}",
                f"runtime_validation_overall={runtime_overall}",
                f"runtime_validation_failed_step={runtime_failed_step}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {focus}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
