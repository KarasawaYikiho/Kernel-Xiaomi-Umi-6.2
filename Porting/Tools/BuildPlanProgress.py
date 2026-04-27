#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from KvUtils import parse_kv, split_csv

ART = Path("artifacts")
PLAN = Path("PortingPlan.md")
OUT = ART / "plan-progress.txt"
OUT_MD = ART / "plan-progress.md"


def normalize_key(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def phase_status_from_marker(value: str) -> str:
    if "✅" in value:
        return "complete"
    if "🔄" in value:
        return "in_progress"
    if "⏳" in value:
        return "pending"
    return normalize_key(value) or "unknown"


def parse_phase_table(lines: list[str]) -> dict[str, str]:
    phases: dict[str, str] = {}
    in_table = False
    for line in lines:
        if line.strip() == "## Phase Status":
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table or not line.startswith("|"):
            continue
        cols = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(cols) < 3 or cols[0] in {"Phase", "-------"}:
            continue
        phases[f"phase_{cols[0]}_status"] = phase_status_from_marker(cols[1])
    return phases


def parse_phase2_checklist(lines: list[str]) -> list[tuple[bool, str]]:
    return parse_phase_checklist(lines, 2)


def parse_phase_checklist(lines: list[str], phase: int) -> list[tuple[bool, str]]:
    items: list[tuple[bool, str]] = []
    in_phase = False
    in_checklist = False
    phase_heading = re.compile(rf"^## Phase {phase}(?::|$)")
    for line in lines:
        stripped = line.strip()
        if phase_heading.match(stripped):
            in_phase = True
            in_checklist = False
            continue
        if in_phase and stripped.startswith("## "):
            break
        if not in_phase:
            continue
        if stripped in {"Checklist:", "## Phase 2 Checklist"}:
            in_checklist = True
            continue
        if not in_checklist:
            continue
        match = re.match(r"- \[(x| )\] (.+)$", stripped, flags=re.IGNORECASE)
        if not match:
            continue
        item = match.group(2).strip().replace("`", "")
        items.append((match.group(1).lower() == "x", item))
    return items


def derive_evidence_status(item: str, report: dict[str, str]) -> tuple[str, str]:
    pending = set(split_csv(report.get("rom_alignment_pending", "")))
    key = normalize_key(item)

    if key == "release_grade_boot_img":
        if (
            report.get("bootimg_status") == "ok"
            and report.get("bootimg_official_reference_gate") == "yes"
        ):
            return "complete", "bootimg_ready_with_official_reference_gate"
        return "pending", report.get("bootimg_reason", "bootimg_not_ready")

    if key == "rom_aligned_boot_dtbo_vbmeta_consistency_checks":
        required = {
            "rom_boot_chain_consistency",
            "rom_dtbo_consistency",
            "rom_vbmeta_consistency",
        }
        if not pending.intersection(required):
            return "complete", "rom_alignment_manifest_integrated"
        return "pending", "rom_alignment_manifest_pending"

    if key == "resolve_dtb_manifest_to_build_mismatches":
        if report.get("manifest_miss", "0") == "0" and report.get(
            "manifest_wanted", "0"
        ) not in ("0", ""):
            return "complete", "dtb_manifest_matches_build"
        return "pending", "dtb_manifest_mismatch_remaining"

    if key in {
        "build_workflow_targets_the_6_target_tree",
        "build_workflow_targets_the_checked_out_kernel_source_tree",
    }:
        if report.get("defconfig_rc") == "0" and report.get("build_rc") == "0":
            return "complete", "checked_out_tree_build_succeeded"
        return "pending", "awaiting_ci_evidence_for_target_workflow"

    if key in {"ci_evidence_confirms_dtbs_rc_0", "local_evidence_confirms_dtbs_rc_0"}:
        if report.get("dtbs_rc") == "0":
            return "complete", "dtbs_rc_zero"
        return "pending", f"dtbs_rc={report.get('dtbs_rc', 'n/a')}"

    if key == "phase_2_report_has_no_required_blockers":
        if report.get("phase2_complete") == "yes":
            return "complete", "phase2_complete"
        if (
            report.get("defconfig_rc") == "0"
            and report.get("build_rc") == "0"
            and report.get("dtbs_rc") == "0"
            and report.get("bootimg_status") == "ok"
            and report.get("bootimg_official_reference_gate") == "yes"
            and report.get("anykernel_validate_status") == "ok"
        ):
            return "complete", "current_phase2_evidence_has_no_required_blockers"
        return "pending", report.get("phase2_blockers", "phase2_not_complete")

    if key == "update_porting_changelog_md_with_phase_2_milestone_evidence":
        return "pending", "changelog_update_required"

    if key == "device_side_runtime_validation_on_official_rom_environment":
        overall = report.get("runtime_validation_overall", "UNKNOWN")
        if overall == "PASS":
            return "complete", "runtime_validation_pass"
        if overall == "FAIL":
            return "in_progress", "runtime_validation_failed"
        return "pending", report.get(
            "runtime_validation_status", "awaiting_device_validation"
        )

    return "unknown", "no_evidence_rule"


def phase_next_gap(checklist: list[tuple[bool, str]]) -> str:
    for checked, item in checklist:
        if not checked:
            return normalize_key(item)
    return ""


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    lines = PLAN.read_text(encoding="utf-8").splitlines() if PLAN.exists() else []
    phase_table = parse_phase_table(lines)
    checklist = parse_phase2_checklist(lines)
    phase3_checklist = parse_phase_checklist(lines, 3)
    phase4_checklist = parse_phase_checklist(lines, 4)
    report = parse_kv(ART / "phase2-report.txt")
    build_exit = parse_kv(ART / "build-exit.txt")
    dtb = parse_kv(ART / "dtb-postcheck.txt")
    boot = parse_kv(ART / "bootimg-info.txt")
    anykernel_validate = parse_kv(ART / "anykernel-validate.txt")

    # BuildPlanProgress runs before BuildPhase2Report in postprocess. Merge the
    # current low-level evidence so checklist decisions do not depend on a stale
    # phase2-report.txt from an earlier run.
    for key in ("defconfig_rc", "build_rc", "dtbs_rc"):
        if key in build_exit:
            report[key] = build_exit[key]
    if "wanted" in dtb:
        report["manifest_wanted"] = dtb["wanted"]
    if "miss" in dtb:
        report["manifest_miss"] = dtb["miss"]
    if "status" in boot:
        report["bootimg_status"] = boot["status"]
    if "official_reference_gate" in boot:
        report["bootimg_official_reference_gate"] = boot["official_reference_gate"]
    if "status" in anykernel_validate:
        report["anykernel_validate_status"] = anykernel_validate["status"]

    completed = 0
    remaining_items: list[str] = []
    checklist_lines: list[str] = []
    out_lines = [f"plan_present={'yes' if PLAN.exists() else 'no'}"]

    for phase in range(5):
        out_lines.append(
            f"phase_{phase}_status={phase_table.get(f'phase_{phase}_status', 'unknown')}"
        )

    for checked, item in checklist:
        item_key = normalize_key(item)
        source = "plan"
        if checked:
            status = "complete"
            reason = "checked_in_plan"
        else:
            status, reason = derive_evidence_status(item, report)
            source = "artifact"

        if status == "complete":
            completed += 1
        else:
            remaining_items.append(item_key)

        out_lines.extend(
            [
                f"checklist_{item_key}_status={status}",
                f"checklist_{item_key}_source={source}",
                f"checklist_{item_key}_reason={reason}",
            ]
        )
        checklist_lines.append(
            f"- [{'x' if status == 'complete' else ' '}] {item} ({status}; {source}: {reason})"
        )

    total = len(checklist)
    remaining = max(total - completed, 0)
    out_lines.extend(
        [
            f"phase_2_checklist_total={total}",
            f"phase_2_checklist_completed={completed}",
            f"phase_2_checklist_remaining={remaining}",
            f"phase_2_next_gap={(remaining_items[0] if remaining_items else '')}",
            f"phase_3_checklist_total={len(phase3_checklist)}",
            f"phase_3_next_gap={phase_next_gap(phase3_checklist)}",
            f"phase_4_checklist_total={len(phase4_checklist)}",
            f"phase_4_next_gap={phase_next_gap(phase4_checklist)}",
            "phase_4_blocked_by=phase_2,phase_3",
        ]
    )

    md_lines = [
        "# Plan Progress",
        "",
        f"- Plan file: `{'present' if PLAN.exists() else 'missing'}`",
        f"- Phase 0: `{phase_table.get('phase_0_status', 'unknown')}`",
        f"- Phase 1: `{phase_table.get('phase_1_status', 'unknown')}`",
        f"- Phase 2: `{phase_table.get('phase_2_status', 'unknown')}`",
        f"- Phase 3: `{phase_table.get('phase_3_status', 'unknown')}`",
        f"- Phase 4: `{phase_table.get('phase_4_status', 'unknown')}`",
        f"- Phase 2 checklist: `{completed}/{total}` complete",
        f"- Next gap: `{remaining_items[0] if remaining_items else 'none'}`",
        f"- Phase 3 next gap: `{phase_next_gap(phase3_checklist) or 'none'}`",
        "- Phase 4 blocked by: `phase_2,phase_3`",
        "",
        "## Phase 2 Checklist",
        *checklist_lines,
        "",
    ]

    OUT.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
