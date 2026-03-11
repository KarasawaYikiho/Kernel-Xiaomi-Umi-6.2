#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "next-focus.txt"


def parse_kv(path: Path) -> dict[str, str]:
    kv: dict[str, str] = {}
    if not path.exists():
        return kv
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    return kv


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)

    report = parse_kv(ART / "phase2-report.txt")
    flash = report.get("flash_status", "unknown")
    anyk = report.get("anykernel_ok", "no")
    anyk_val = report.get("anykernel_validate_status", "unknown")
    hit_ratio = float(report.get("manifest_hit_ratio", "0") or 0)
    build_rc = report.get("build_rc", "n/a")
    dtbs_rc = report.get("dtbs_rc", "n/a")
    report_next = report.get("next_action", "")

    focus = "collect-more-data"
    reason = "default"

    # Prefer phase2-report decision when present to keep postprocess outputs consistent.
    if report_next == "fix-defconfig-errors":
        focus = "fix-defconfig-errors"
        reason = "report_next_action"
    elif report_next == "fix-build-errors":
        focus = "fix-build-errors"
        reason = "report_next_action"
    elif report_next == "fix-dtb-build-errors":
        focus = "fix-dtb-errors"
        reason = "report_next_action"
    elif report_next == "fix-anykernel-packaging":
        focus = "fix-anykernel-packaging"
        reason = "report_next_action"
    elif report_next == "ready-for-action-test":
        focus = "request-action-validation"
        reason = "report_next_action"
    elif report_next == "prepare-release-bootimg":
        focus = "prepare-release-bootimg"
        reason = "report_next_action"
    elif build_rc not in ("0", "n/a"):
        focus = "fix-build-errors"
        reason = "core_build_failed"
    elif dtbs_rc not in ("0", "n/a"):
        focus = "fix-dtb-errors"
        reason = "dtb_build_failed"
    elif flash == "candidate" and anyk != "yes":
        focus = "fix-anykernel-packaging"
        reason = "candidate_without_anykernel"
    elif flash == "candidate" and anyk == "yes" and anyk_val not in ("ok", "unknown"):
        focus = "fix-anykernel-packaging"
        reason = "candidate_with_invalid_anykernel_structure"
    elif flash == "candidate" and anyk == "yes":
        focus = "request-action-validation"
        reason = "candidate_and_packaging_ok"
    elif hit_ratio < 0.35:
        focus = "improve-dtb-manifest-mapping"
        reason = "low_manifest_hit_ratio"

    OUT.write_text(
        "\n".join([
            f"focus={focus}",
            f"reason={reason}",
            f"flash_status={flash}",
            f"anykernel_ok={anyk}",
            f"anykernel_validate_status={anyk_val}",
            f"manifest_hit_ratio={hit_ratio:.3f}",
            f"build_rc={build_rc}",
            f"dtbs_rc={dtbs_rc}",
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT}: {focus}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
