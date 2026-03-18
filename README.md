# Kernel-Xiaomi-Umi

[中文文档（README.zh-CN.md）](./README.zh-CN.md)

Kernel-Xiaomi-Umi is a **porting orchestrator** for Xiaomi 10 (`umi`) kernel migration.
It focuses on CI workflow automation, diagnostics, and reproducible delivery artifacts.

> This repository is **not** a full kernel source tree.

## Repository Scope

- Run CI-based porting/build workflows
- Execute Phase2 migration from SO-TS 4.19 toward a 5+ baseline
- Produce structured diagnostics (`phase2-report`, `next-focus`, metrics, consistency checks)
- Produce flash candidates (`AnyKernel3-umi-candidate.zip`) and release-oriented `boot.img` readiness outputs

## Final Delivery Target

1. Generate a **release-grade, directly flashable `boot.img`** for Xiaomi 10 (`umi`).
2. Keep **same-model reproducibility in GitHub Actions** (same inputs -> same deterministic output category).
3. Preserve full CI evidence for every run (report, errors, metrics, checklist).

## Upstream / Reference Inputs

- SO-TS source reference: <https://github.com/SO-TS/android_kernel_xiaomi_sm8250>
- Additional donor/comparison references:
  - `UtsavBalar1231/android_kernel_xiaomi_sm8150`
  - `UtsavBalar1231/display-drivers`
  - `UtsavBalar1231/camera-kernel`
  - `liyafe1997` (Strawing author-ID discovery source)

Rules:
- Author IDs are discovery inputs; repositories must be explicitly selected before integration.
- References are used for targeted adaptation, **never** blind subtree copy.
- No proprietary ROM blobs are imported into this repo.

## Official ROM Baseline (Analysis Only)

- Baseline package: `D:\GIT\MIUI_UMI_OS1.0.5.0.TJBCNXM_d01651ed86_13.0.zip`
- Analysis file: `Porting/OfficialRom-Umi-Os1.0.5.0-Analysis.md`
- Scope: metadata/hash/partition-op evidence only

## Main Workflows

> CI compatibility: workflows set `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true`.

### Quick Start (Recommended)

Run **`Phase2-Port-Umi.yml`** with default inputs, then inspect artifacts in this order:

1. `artifacts/runtime-validation-summary.md`
2. `artifacts/runtime-validation-input.md`
3. `artifacts/runtime-validation-result.txt`
4. `artifacts/phase2-report.txt`
5. `artifacts/status-badge-line.txt`
6. `artifacts/action-validation-checklist.md`
7. `artifacts/artifact-summary.md`
8. `artifacts/next-focus.txt`
9. `artifacts/build-error-summary.txt`
10. `artifacts/anykernel-info.txt`

Runtime gate note:
- `driver_integration_status=partial` does **not** automatically block device runtime validation.
- If `next_action=ready-for-action-test` and `runtime_ready=yes`, remaining `driver_integration_pending` items are treated as release / ROM-alignment follow-ups unless they appear in the runtime blocker list.

### `Phase2-Port-Umi.yml`

Core migration workflow. Typical stages:

1. Dependency/tool bootstrap
2. Source + target prep
3. Phase2 migration apply
4. Kernel build attempt
5. Artifact collection + packaging
6. Postprocess (report/metrics/consistency/checklist)

Important inputs:

- `device` (default `umi`)
- `source_repo` / `target_repo`
- `bootimg_ramdisk_url` (optional)
- `bootimg_prebuilt_url` (optional fallback)
- `bootimg_required_bytes` (default `134217728`; set `<=0` to disable size check)

After device runtime validation:
- Fill `artifacts/runtime-validation-input.md`
- Re-run postprocess to refresh `runtime-validation-result.txt`, `phase2-report.txt`, `next-focus.txt`, badge, metrics, and summaries
- If runtime validation passes, the decision flow automatically shifts from `ready-for-action-test` into release hardening (`prepare-release-bootimg`) or remaining ROM / driver alignment follow-up (`integrate-drivers-phase3`)
- For local rule changes, run `python Tools/Porting/Selftest_Decision_Flow.py` before pushing

### `Build-Umi-Kernel.yml`

Reference cloud build path:

1. Install deps / ccache
2. Fetch toolchain
3. Clone target repo
4. Run `build.sh`
5. Upload artifacts

## Documentation Map

- `PORTING_PLAN.md` — roadmap and phase status
- `Porting/README.md` — planning/baseline docs index
- `Tools/Porting/README.md` — script index and CI pipeline details
- `CONTRIBUTING.md` — contribution policy
- `SECURITY.md` — vulnerability reporting policy

## License

GPL-2.0-only
