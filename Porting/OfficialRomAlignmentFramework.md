# Official ROM Alignment Framework

## Purpose

This project builds a yefxx-based Linux 6.11 `umi` kernel from source.

The official Xiaomi ROM is used as a reference extraction source and validation baseline for release-chain alignment, not as the target kernel version and not as a code donor.

## Scope

The ROM alignment framework covers only compatibility-facing checkpoints:

- release-grade `boot.img` packaging
- `boot` / `dtbo` / `vbmeta` consistency against official baseline evidence
- dynamic partition baseline awareness
- DTB target coverage required by the current manifest
- runtime validation on official userspace

It does not redefine the project target away from the yefxx-based source kernel baseline.

## Core Backlog

The framework tracks the following work items through `artifacts/rom-alignment-manifest.txt`:

- `bootimg_release_packaging`
- `rom_boot_chain_consistency`
- `rom_dtbo_consistency`
- `rom_vbmeta_consistency`
- `rom_dynamic_partition_baseline`
- `dtb_target_coverage`
- `runtime_validation_official_rom`

## Evidence Sources

The ROM alignment status is derived from existing artifacts:

- `Porting/OfficialRomAnalysis.md`
- `artifacts/bootimg-info.txt`
- `artifacts/dtb-postcheck.txt`
- `artifacts/driver-integration-evidence.txt`
- `artifacts/runtime-validation-result.txt`

## Execution Flow

1. Initialize `rom-alignment-manifest.txt`
2. Sync completed items from current artifact evidence
3. Validate manifest format
4. Build `rom-alignment-status.txt`
5. Feed status into `phase2-report.txt`

## Near-Term Priorities

1. Make release `boot.img` generation reproducible in CI
2. Stop treating official ROM comparison as optional bookkeeping
3. Resolve DTB manifest-to-build mismatches before expanding runtime scope
4. Finish device-side runtime validation on official ROM userspace
