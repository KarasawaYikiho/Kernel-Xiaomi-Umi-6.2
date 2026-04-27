#!/usr/bin/env python3
from pathlib import Path

ART = Path("artifacts")
OUT = ART / "runtime-validation-input.md"


OLD_TEMPLATE_REPLACEMENTS = {
    "Fill this file after device-side validation of the fastboot-booted or Magisk-patched boot image. Keep each result on one line.": "Fill this file after device-side validation of the temporary fastboot-booted image. Keep each result on one line.",
    "# meta.patched_boot_image=magisk_patched-28000_abc123.img": "# meta.patched_boot_image=boot-test-28000_abc123.img",
    "check.boot_flash=UNKNOWN": "check.temporary_boot=UNKNOWN",
    "# check.boot_flash=PASS": "# check.temporary_boot=PASS",
}


def migrate_existing_template(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    migrated = text
    for old, new in OLD_TEMPLATE_REPLACEMENTS.items():
        migrated = migrated.replace(old, new)
    if migrated == text:
        return False
    path.write_text(migrated, encoding="utf-8")
    return True


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        if migrate_existing_template(OUT):
            print(f"updated existing {OUT}")
            return 0
        print(f"kept existing {OUT}")
        return 0

    lines = [
        "# Runtime Validation Input",
        "",
        "Fill this file after device-side validation of the temporary fastboot-booted image. Keep each result on one line.",
        "Use: PASS / FAIL / SKIP / UNKNOWN",
        "",
        "meta.overall=UNKNOWN",
        "meta.failed_step=",
        "meta.boot_method=fastboot_boot",
        "meta.patched_boot_image=",
        "meta.stock_boot_backup_sha256=",
        "meta.stock_dtbo_backup_sha256=",
        "meta.stock_vbmeta_backup_sha256=",
        "meta.stock_vbmeta_system_backup_sha256=",
        "meta.notes=",
        "meta.dmesg=",
        "meta.logcat=",
        "meta.pstore=",
        "",
        "preflight.bootloader_unlocked=UNKNOWN",
        "preflight.rom_matches_baseline=UNKNOWN",
        "preflight.stock_partitions_backed_up=UNKNOWN",
        "preflight.fastboot_boot_supported=UNKNOWN",
        "preflight.current_slot_recorded=UNKNOWN",
        "preflight.rollback_package_ready=UNKNOWN",
        "",
        "check.temporary_boot=UNKNOWN",
        "check.first_boot=UNKNOWN",
        "check.uname=UNKNOWN",
        "check.connectivity=UNKNOWN",
        "check.audio=UNKNOWN",
        "check.camera=UNKNOWN",
        "check.touch=UNKNOWN",
        "check.charging=UNKNOWN",
        "check.thermal=UNKNOWN",
        "check.idle_stability=UNKNOWN",
        "check.light_load_stability=UNKNOWN",
        "",
        "# Example:",
        "# meta.overall=FAIL",
        "# meta.failed_step=check.audio",
        "# meta.boot_method=fastboot_boot",
        "# meta.patched_boot_image=boot-test-28000_abc123.img",
        "# meta.stock_boot_backup_sha256=...",
        "# meta.stock_dtbo_backup_sha256=...",
        "# meta.stock_vbmeta_backup_sha256=...",
        "# meta.notes=speaker silent but bluetooth audio ok",
        "# meta.dmesg=attached in chat",
        "# meta.logcat=attached in chat",
        "# meta.pstore=attached in chat if present",
        "# preflight.bootloader_unlocked=PASS",
        "# preflight.rom_matches_baseline=PASS",
        "# preflight.stock_partitions_backed_up=PASS",
        "# preflight.fastboot_boot_supported=PASS",
        "# preflight.current_slot_recorded=PASS",
        "# preflight.rollback_package_ready=PASS",
        "# check.temporary_boot=PASS",
        "# check.first_boot=PASS",
        "# check.uname=PASS",
        "# check.connectivity=PASS",
        "# check.audio=FAIL",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
