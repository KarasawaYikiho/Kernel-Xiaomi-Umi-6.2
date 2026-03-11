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
    anyk_val = parse_kv(ART / "anykernel-validate.txt")
    boot = parse_kv(ART / "bootimg-info.txt")
    boot_build = parse_kv(ART / "bootimg-build.txt")
    missa = parse_kv(ART / "dtb-miss-analysis.txt")
    bexit = parse_kv(ART / "build-exit.txt")
    complete = parse_kv(ART / "artifact-completeness.txt")

    # derive a simple decision hint for next step automation
    flash_status = flash.get('status', 'unknown')
    anykernel_ok = anyk.get('anykernel_ok', 'no')
    hit_ratio = dtb.get('hit_ratio', '0.000')
    def_rc = bexit.get('defconfig_rc', 'n/a')
    build_rc = bexit.get('build_rc', 'n/a')
    dtbs_rc = bexit.get('dtbs_rc', 'n/a')

    anyk_val_status = anyk_val.get('status', 'unknown')
    next_action = 'collect-more-data'
    if def_rc not in ('0', 'n/a'):
        next_action = 'fix-defconfig-errors'
    elif build_rc not in ('0', 'n/a'):
        next_action = 'fix-build-errors'
    elif dtbs_rc not in ('0', 'n/a'):
        next_action = 'fix-dtb-build-errors'
    elif flash_status == 'candidate' and anykernel_ok == 'yes' and anyk_val_status in ('ok', 'unknown'):
        next_action = 'ready-for-action-test'

    if boot.get('status', 'missing') in ('missing', 'size_mismatch'):
        next_action = 'prepare-release-bootimg'
    elif flash_status == 'candidate' and (anykernel_ok != 'yes' or anyk_val_status not in ('ok', 'unknown')):
        next_action = 'fix-anykernel-packaging'

    runtime_ready = 'yes' if next_action == 'ready-for-action-test' else 'no'

    lines = [
        "phase2_report=1",
        f"device={pack.get('device', summary.get('device', 'unknown'))}",
        f"defconfig_rc={bexit.get('defconfig_rc', 'n/a')}",
        f"build_rc={bexit.get('build_rc', 'n/a')}",
        f"dtbs_rc={bexit.get('dtbs_rc', 'n/a')}",
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
        f"anykernel_validate_status={anyk_val.get('status', 'unknown')}",
        f"anykernel_validate_reason={anyk_val.get('reason', 'n/a')}",
        f"bootimg_status={boot.get('status', 'missing')}",
        f"bootimg_reason={boot.get('reason', 'n/a')}",
        f"bootimg_size_bytes={boot.get('size_bytes', '0')}",
        f"bootimg_required_bytes={boot.get('required_bytes', '268435456')}",
        f"bootimg_size_match={boot.get('size_match', 'no')}",
        f"bootimg_build_status={boot_build.get('status', 'unknown')}",
        f"bootimg_build_reason={boot_build.get('reason', 'n/a')}",
        f"bootimg_build_missing={boot_build.get('missing', '')}",
        f"miss_bucket_total={missa.get('bucket_total', '0')}",
        f"miss_top_buckets={missa.get('top_buckets', '')}",
        f"artifact_completeness={complete.get('status', 'unknown')}",
        f"required_missing={complete.get('required_missing', 'n/a')}",
        f"next_action={next_action}",
        f"runtime_ready={runtime_ready}",
    ]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
