# UMI Kernel Porting Plan (SO-TS 4.19 -> 5+)

## Mission

Migrate device capability from `SO-TS/android_kernel_xiaomi_sm8250` (4.19) onto a 5+ baseline with CI-first reproducibility.

## Final Repository Goal

- Deliver a **release-grade, directly flashable `boot.img`**.
- Keep **GitHub Actions reproducibility** for the same model + same workflow inputs.

## Reference Sources

- SO-TS: <https://github.com/SO-TS/android_kernel_xiaomi_sm8250>
- 5+ baseline candidate: <https://github.com/yefxx/xiaomi-umi-linux-kernel>
- Driver donor references:
  - <https://github.com/UtsavBalar1231/android_kernel_xiaomi_sm8150>
  - <https://github.com/UtsavBalar1231/display-drivers>
  - <https://github.com/UtsavBalar1231/camera-kernel>
- Author-ID discovery source: `liyafe1997` (Strawing)

Policy:
- Author IDs are discovery inputs, not direct integration targets.
- No blind full-tree copy from references.
- Official ROM packages are analysis-only (no proprietary blob import).

## Current Snapshot

- Phase 0: Complete
- Phase 1: Complete
- Phase 2: In progress (automated migration + diagnostics + packaging)
- Current focus: runtime validation feedback loop + release `boot.img` hardening

## Phase Checklist

### Phase 0 — Baseline Lock
- [x] Lock baseline source/target
- [x] Define branch strategy (`port/phase-*`)

### Phase 1 — Capability Inventory
- [x] Extract SO-TS capability inventory (defconfig/dts/techpack/patch)
- [x] Extract 5+ baseline inventory
- [x] Generate migration classification report

### Phase 2 — Minimal Bootable Migration
- [x] Automated defconfig migration
- [x] Automated DTS/DTSI seed migration
- [x] CI build + AnyKernel candidate packaging
- [ ] Release-grade `boot.img` output with size/partition constraints

### Phase 3 — Feature Completion
- [ ] Display / refresh-rate path
- [ ] Audio / sensor path
- [ ] Optional KernelSU integration
- [ ] MIUI-specific capability adaptation where feasible

### Phase 4 — Stability & Regression
- [ ] Daily-use regression pass
- [ ] Power / thermal / stability comparison
- [ ] Release candidate sign-off

## Execution Rules

- At least one compilable commit per phase.
- Every push should have CI evidence.
- Major changes must update `Porting/CHANGELOG.md`.
