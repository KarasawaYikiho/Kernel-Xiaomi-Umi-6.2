#!/usr/bin/env python3
from pathlib import Path

from KvUtils import parse_kv
from Phase2Decision import derive_runtime_ready, derive_next_focus

ART = Path("artifacts")
OUT = ART / "decision-consistency.txt"


def to_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    report = parse_kv(ART / "phase2-report.txt")
    focus = parse_kv(ART / "next-focus.txt")

    next_action = report.get("next_action", "collect-more-data")
    runtime_ready = report.get("runtime_ready", "no")
    expected_runtime = derive_runtime_ready(next_action)

    expected_focus, _ = derive_next_focus(
        report_next_action=next_action,
        artifact_completeness=report.get("artifact_completeness", "unknown"),
        build_context_present=report.get("build_context_present", "unknown"),
        build_rc=report.get("build_rc", "n/a"),
        dtbs_rc=report.get("dtbs_rc", "n/a"),
        flash_status=report.get("flash_status", "unknown"),
        anykernel_ok=report.get("anykernel_ok", "no"),
        anykernel_validate_status=report.get("anykernel_validate_status", "unknown"),
        manifest_hit_ratio=to_float(report.get("manifest_hit_ratio", "0"), 0.0),
        rom_alignment_status=report.get("rom_alignment_status", "pending"),
        rom_alignment_pending=report.get("rom_alignment_pending", ""),
        runtime_validation_overall=report.get("runtime_validation_overall", "UNKNOWN"),
        runtime_validation_failed_step=report.get("runtime_validation_failed_step", ""),
    )
    actual_focus = focus.get("focus", "")

    errors = []
    if runtime_ready != expected_runtime:
        errors.append(f"runtime_ready_mismatch:{runtime_ready}->{expected_runtime}")
    if actual_focus and actual_focus != expected_focus:
        errors.append(f"focus_mismatch:{actual_focus}->{expected_focus}")

    status = "ok" if not errors else "invalid"
    OUT.write_text(
        "\n".join(
            [
                f"status={status}",
                f"next_action={next_action}",
                f"runtime_ready={runtime_ready}",
                f"expected_runtime_ready={expected_runtime}",
                f"focus={actual_focus}",
                f"expected_focus={expected_focus}",
                f"errors={','.join(errors)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
