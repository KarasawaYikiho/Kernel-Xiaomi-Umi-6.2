# SM8250 Kernel Porting Plan

## Mission

Migrate Xiaomi SM8250-family kernels from the SO-TS 4.19 source baseline to a 6+ target kernel baseline with reproducible CI evidence, using `umi` as the current ROM-alignment reference device.

## Goals

- Build from the 6+ target tree: `yefxx/xiaomi-umi-linux-kernel`.
- Keep SO-TS 4.19 as a migration source, not as the build target.
- Produce a release-grade flashable `boot.img` with official ROM baseline evidence.
- Keep GitHub Actions reproducible and artifact-driven.
- Defer all real-device flashing and runtime validation until Phase 2 is complete.

## Official ROM Alignment Principle

This project targets a 6+ kernel baseline built from source for Xiaomi SM8250-family devices, with `umi` serving as today's reference ROM-alignment sample.

The official Xiaomi ROM is used only as a reference extraction source and validation baseline for:

- `boot.img` size and packaging constraints
- `dtbo` / `vbmeta` / dynamic partition expectations
- boot-chain consistency checks
- runtime validation on official userspace after CI gates are complete

The official ROM is not the target kernel version and must not be treated as a code donor.

## References

- Source baseline: `SO-TS/android_kernel_xiaomi_sm8250` (`android16-aptusitu`, 4.19)
- Target baseline: `yefxx/xiaomi-umi-linux-kernel` (`master`, 6+ target)
- Driver donors: `UtsavBalar1231/*`
- Reference device: `umi`
- Official ROM baseline: `V816.0.5.0.TJBCNXM`
- Unified config: `Porting/Sm8250PortConfig.json`

## Hard Gate: No Real-Device Testing Before Phase 2 Completion

Real-device flashing, Magisk-patched boot validation, and official-ROM runtime validation are forbidden while any Phase 2 exit criterion remains incomplete.

Phase 2 must finish first because current artifacts can produce a release-ready `boot.img` while still reporting build and DTB blockers. A flashable artifact is not enough evidence for device-side testing.

## Phase Status

| Phase | Status | Description |
|-------|--------|-------------|
| 0 | Complete | Baseline lock |
| 1 | Complete | Capability inventory |
| 2 | In Progress | 6+ migration, CI build, packaging, and ROM alignment gates |
| 3 | Pending | Kernel usability and feature completion |
| 4 | Pending | Device runtime validation, stability, and regression |

## Current Evidence Snapshot

Latest analyzed artifact: `rom-aligned-umi-2.zip` from run `2`.

Observed state:

- `defconfig_rc=0`
- `build_rc=0`
- `dtbs_rc=2`
- `flash_status=candidate`
- `release_status=ready`
- `anykernel_ok=yes`
- `anykernel_validate_status=ok`
- `bootimg_status=ok`
- `bootimg_size_match=yes`
- `bootimg_rom_sha256_match=yes`
- `bootimg_rom_header_version_match=yes`
- `bootimg_official_reference_gate=yes`
- `phase2_report_state=not_ready`
- `runtime_ready=no`
- `next_action=fix-dtb-build-errors`

Current required blocker:

- DTB build / manifest mismatch remains, with latest misses reported as:
  - `kona-7230-iot-rb5.dtb`
  - `kona-7230m-iot-rb5.dtb`
  - `kona-v2.1-iot-rb5.dtb`
  - `xiaomi-sm8250-common.dtb`

Current Phase 3 usability follow-up:

- `camera_isp_path`

## Phase 0: Baseline Lock

Status: Complete.

Exit evidence:

- `Porting/BaselineLock.json` pins the source and target repositories.
- `Porting/Sm8250PortConfig.json` centralizes repo URLs, branches, toolchain source, supported devices, and ROM baseline paths.

## Phase 1: Capability Inventory

Status: Complete.

Exit evidence:

- `Porting/Inventory.json` records source, target, and donor inventory.
- `Porting/GapReport.md` identifies the defconfig, DTS, and techpack gaps.
- `Porting/ReferenceDriversAnalysis.md` identifies `cam_sensor_module` and camera-related paths as the first usability focus.

## Phase 2: CI Migration, Packaging, and ROM Alignment

Status: In Progress.

Purpose: produce a CI-clean, ROM-aligned artifact set from the 6+ target flow before any real-device testing.

Checklist:

- [x] Automated defconfig migration
- [x] Automated DTS/DTSI seed
- [x] CI build + AnyKernel packaging
- [x] Release-grade `boot.img`
- [x] ROM-aligned boot / `dtbo` / `vbmeta` consistency checks
- [ ] Build workflow targets the 6+ target tree
- [ ] Resolve DTB manifest-to-build mismatches
- [ ] CI evidence confirms `dtbs_rc=0`
- [ ] Phase 2 report has no required blockers
- [ ] Update `Porting/CHANGELOG.md` with Phase 2 milestone evidence

Immediate work:

1. Ensure `Build-Umi-Kernel.yml` builds from `TARGET_REPO` and `TARGET_BRANCH`, not `SOURCE_REPO` and `SOURCE_BRANCH`.
2. Tighten DTB manifest generation so non-current-device IoT RB5 boards and weak common aliases do not block Umi Phase 2.
3. Run local selftests and repository sanity checks.
4. Rerun `ROM-Aligned-Umi-Port.yml` for `umi`.
5. Inspect the new artifact set before changing Phase 2 status.

Phase 2 exit criteria:

- `defconfig_rc=0`
- `build_rc=0`
- `dtbs_rc=0`
- `bootimg_status=ok`
- `bootimg_official_reference_gate=yes`
- `anykernel_validate_status=ok`
- `phase2_report_state` is not blocked by required Phase 2 items
- `next_action` is not `fix-dtb-build-errors`
- `runtime_ready` may remain `no` if Phase 3 usability work is still pending

Required local verification before CI rerun:

```bash
python Tools/Porting/SelftestBuildWorkflow.py
python Tools/Porting/SelftestDtbManifest.py
python Tools/Porting/SelftestDecisionFlow.py
python Tools/Porting/RepoSanityCheck.py
python -m compileall Tools/Porting
```

## Phase 3: Kernel Usability and Feature Completion

Status: Pending.

Purpose: clear kernel usability blockers after Phase 2 is CI-clean. Phase 3 is still not a real-device testing phase.

Checklist:

- [ ] Analyze `camera_isp_path` as the first usability blocker.
- [ ] Map required camera ISP Kconfig symbols.
- [ ] Map required camera ISP Makefile entries.
- [ ] Map required DTS compatible strings and include paths.
- [ ] Compare source, target, and donor references for only the required deltas.
- [ ] Integrate required driver pieces into the 6+ target layout without blind techpack subtree copy.
- [ ] Update driver integration evidence artifacts.
- [ ] Confirm `driver_integration_pending` has no runtime-blocking usability gaps.
- [ ] Update `Porting/CHANGELOG.md` with Phase 3 evidence.

Phase 3 exit criteria:

- Phase 2 is complete.
- `driver_integration_status=complete`, or remaining pending items are documented as non-runtime-blocking.
- CI still reports `defconfig_rc=0`, `build_rc=0`, and `dtbs_rc=0`.
- Artifact reports identify no required blockers before runtime validation.

## Phase 4: Runtime Validation, Stability, and Regression

Status: Pending.

Purpose: validate the Phase 2 + Phase 3 artifact on official ROM userspace and harden regressions found during runtime testing.

Phase 4 may start only after Phase 2 and Phase 3 exit criteria are met.

Checklist:

- [ ] Prepare the Magisk-patched boot validation package.
- [ ] Record patched boot image filename and hash.
- [ ] Flash only after rollback path is confirmed.
- [ ] Boot official ROM userspace with the validated artifact.
- [ ] Collect dmesg and logcat evidence.
- [ ] Fill runtime validation result input.
- [ ] Rerun postprocess suite with runtime results.
- [ ] Confirm `runtime_validation_overall=PASS`.
- [ ] Triage and fix regressions with test or artifact evidence.
- [ ] Update `Porting/CHANGELOG.md` with runtime validation evidence.

## Execution Rules

- Phase 2 must complete before any real-device testing.
- Phase 4 must not start until Phase 2 and Phase 3 exit criteria are met.
- One compilable commit per phase-sized change.
- Every push requires CI evidence.
- Major changes update `Porting/CHANGELOG.md`.
- Official ROM artifacts are validation inputs only, not kernel code donors.
- Donor repositories may be used only for targeted deltas with evidence.
- No blind subtree copy from legacy techpack.
- Prefer artifact evidence over assumptions when updating status.
