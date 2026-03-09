#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "phase2-report.txt"


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

    summary = parse_kv(ART / "summary.txt")
    pack = parse_kv(ART / "umi_bundle" / "pack-info.txt")
    flash = parse_kv(ART / "flash-readiness.txt")
    dtb = parse_kv(ART / "dtb-postcheck.txt")
    anyk = parse_kv(ART / "anykernel-info.txt")
    missa = parse_kv(ART / "dtb-miss-analysis.txt")

    # derive a simple decision hint for next step automation
    flash_status = flash.get('status', 'unknown')
    anykernel_ok = anyk.get('anykernel_ok', 'no')
    hit_ratio = dtb.get('hit_ratio', '0.000')
    next_action = 'collect-more-data'
    if flash_status == 'candidate' and anykernel_ok == 'yes':
        next_action = 'ready-for-action-test'
    elif flash_status == 'candidate' and anykernel_ok != 'yes':
        next_action = 'fix-anykernel-packaging'

    lines = [
        "phase2_report=1",
        f"device={pack.get('device', summary.get('device', 'unknown'))}",
        f"dts_copied={summary.get('dts_copied', '0')}",
        f"dts_only_copied={summary.get('dts_only_copied', '0')}",
        f"dtsi_only_copied={summary.get('dtsi_only_copied', '0')}",
        f"umi_bundle_xiaomi_dtb_count={pack.get('umi_bundle_xiaomi_dtb_count', '0')}",
        f"flash_status={flash.get('status', 'unknown')}",
        f"flash_reason={flash.get('reason', 'n/a')}",
        f"manifest_wanted={dtb.get('wanted', '0')}",
        f"manifest_hit={dtb.get('hit', '0')}",
        f"manifest_miss={dtb.get('miss', '0')}",
        f"manifest_hit_ratio={hit_ratio}",
        f"anykernel_ok={anykernel_ok}",
        f"anykernel_has_imagegz={anyk.get('has_imagegz', 'no')}",
        f"anykernel_has_dtb={anyk.get('has_dtb', 'no')}",
        f"anykernel_dtb_source={anyk.get('dtb_source', '')}",
        f"miss_bucket_total={missa.get('bucket_total', '0')}",
        f"miss_top_buckets={missa.get('top_buckets', '')}",
        f"next_action={next_action}",
    ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
