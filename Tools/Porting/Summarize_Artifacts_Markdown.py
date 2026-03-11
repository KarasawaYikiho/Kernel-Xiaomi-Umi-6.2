#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "artifact-summary.md"


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
    r = parse_kv(ART / "phase2-report.txt")
    n = parse_kv(ART / "next-focus.txt")
    c = parse_kv(ART / "artifact-completeness.txt")

    next_action = r.get('next_action', '')

    md = [
        "# Phase2 Artifact Summary",
        "",
        f"- Device: `{r.get('device', 'unknown')}`",
        f"- Build RC: `{r.get('build_rc', 'n/a')}` (defconfig `{r.get('defconfig_rc', 'n/a')}`)",
        f"- Flash Status: `{r.get('flash_status', 'unknown')}`",
        f"- AnyKernel OK: `{r.get('anykernel_ok', 'no')}`",
        f"- AnyKernel Validate: `{r.get('anykernel_validate_status', 'unknown')}` ({r.get('anykernel_validate_reason', 'n/a')})",
        f"- Manifest Hit Ratio: `{r.get('manifest_hit_ratio', '0.000')}`",
        f"- Artifact Completeness: `{c.get('status', 'unknown')}`",
        f"- Runtime Ready: `{r.get('runtime_ready', 'no')}`",
        f"- Boot Image: `{r.get('bootimg_status', 'missing')}` ({r.get('bootimg_reason', 'n/a')})",
        f"- Boot Image Build: `{r.get('bootimg_build_status', 'unknown')}` ({r.get('bootimg_build_reason', 'n/a')})",
        "",
        "## Next Focus",
        f"- Focus: `{n.get('focus', 'collect-more-data')}`",
        f"- Reason: `{n.get('reason', 'n/a')}`",
        "",
        "## Suggested First Files",
        "- `phase2-report.txt`",
        "- `build-error-summary.txt`",
        "- `dtb-postcheck.txt`",
        "- `anykernel-info.txt`",
        "- `anykernel-validate.txt`",
    ]

    if next_action == 'prepare-release-bootimg':
        md.extend([
            "- `bootimg-info.txt`",
            "- `bootimg-build.txt`",
        ])

    if r.get('runtime_ready', 'no') == 'yes':
        md.append("- `action-validation-checklist.md`")

    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
