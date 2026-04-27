# Changelog

> Milestone-only changelog.

## 2026-04-27

- Completed local Phase2 evidence for `umi`: `defconfig_rc=0`, `build_rc=0`, `dtbs_rc=0`, and `phase2_report_state=ready`
- Confirmed DTB manifest/build alignment with 4 wanted DTBs, 4 hits, and 0 misses
- Prepared ROM-aligned reference `boot.img` evidence from the official baseline with `bootimg_status=ok` and `bootimg_official_reference_gate=yes`
- Updated runtime validation guidance to use temporary `fastboot boot` as the first device route and keep Phase3 camera blockers ahead of device testing
- Registered the dual-track reference strategy: yefxx 6.11 remains the experimental mainline build baseline while LineageOS, liyafe, and N0Kernel are targeted reference inputs
- Clarified the boot artifact goal as official-aligned, patcher-agnostic, and compatible with KernelSU and Magisk

## 2026-04-25

- Reframed `PortingPlan.md` around 6+ target builds, Phase2 hard gates, Phase3 usability, and Phase4 runtime validation
- Added Phase2/P3/P4 report wiring so plan progress, phase2 report, ROM alignment, driver integration, and runtime summary use the same phase ownership model
- Added a final Phase2 CI gate through `ValidatePhase2Report.py` while preserving uploaded artifacts for failed/incomplete runs
- Added selftests for target workflow selection, DTB manifest filtering, and phase framework gating

## 2026-04-14

- Fixed workflow script name errors causing exit code 127
- Fixed internal script references (Phase2Apply, etc.)
- Fixed Python comment references (FetchInventory, SyncDriverIntegrationManifest)
- Rewrote all README files for consistency

## 2026-03-26

- Tightened postprocess chain with driver integration evidence
- Preserved runtime-validation-input.md during reruns
- ROM-aware artifact readiness gate
- Added python/python3 auto-detection for Windows compatibility
- Reduced script duplication via Common.sh and KvUtils.py

## 2026-03-11

- Refactored postprocess with centralized KV parser
- Documentation rewrite for consistency

## Legacy

See git history for earlier milestones.
