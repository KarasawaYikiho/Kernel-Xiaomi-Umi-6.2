# Kernel-Xiaomi-Umi

[中文文档（README.zh-CN.md）](./README.zh-CN.md)

Kernel-Xiaomi-Umi is a **porting orchestrator** for Xiaomi 10 (umi) kernel migration work.
It is designed to automate Phase2 migration, CI build attempts, diagnostics, and artifact packaging.

> This repository is **not** a full kernel source tree.

## What this repository does

- Runs CI-based kernel build/porting workflows
- Applies Phase2 migration from SO-TS 4.19 toward a 5+ baseline
- Generates structured diagnostics and decision artifacts
- Produces candidate packaging artifacts (including AnyKernel candidate zip)

## Final Target

- Produce a **release-grade, directly flashable `boot.img`** for Xiaomi 10 (umi).
- Ensure **same-model reproducibility in GitHub Actions**: identical model + identical workflow inputs should compile and produce a flashable artifact.
- Retain Phase2 diagnostics as CI evidence while shifting delivery from "candidate zip" to "release `boot.img` + validation checklist".

## Upstream references

- SO-TS source reference: `SO-TS/android_kernel_xiaomi_sm8250`
- URL: <https://github.com/SO-TS/android_kernel_xiaomi_sm8250>

## Workflows

### Quick Start (recommended)

Run **`phase2-port-umi.yml`** with default inputs, then inspect artifacts in this order:

1. `artifacts/phase2-report.txt`
2. `artifacts/build-exit.txt`
3. `artifacts/build-error-summary.txt`
4. `artifacts/anykernel-info.txt`
5. `artifacts/next-focus.txt`

This provides a fast pass/fail + next-action loop.

### `build-umi-kernel.yml`

Reference-style cloud build flow:

1. Install dependencies + setup ccache
2. Download ZyC Clang 15
3. Clone target kernel repo/branch
4. Run `build.sh` with selected device and optional KernelSU
5. Upload build artifacts

Inputs:

- `kernel_repo`
- `kernel_branch`
- `device` (default: `umi`)
- `ksu` (default: `false`)

### `phase2-port-umi.yml`

Phase2 migration + build + diagnostics flow:

1. Prepare source/target trees
2. Apply Phase2 migration
3. Run core build and DTB-target attempts
4. Collect artifacts and umi-focused package
5. Build AnyKernel candidate
6. Generate reports and upload all artifacts

Inputs:

- `source_repo`
- `source_branch`
- `target_repo`
- `target_branch`
- `device` (default: `umi`)
- `bootimg_required_bytes` (default: `268435456`, i.e. 256MiB)

## Key scripts

Core wrappers / orchestrators:

- `tools/porting/install_ci_deps.sh`
- `tools/porting/prepare_phase2_sources.sh`
- `tools/porting/check_target_kernel_version.sh`
- `tools/porting/apply_phase2_migration.sh`
- `tools/porting/run_phase2_build.sh`
- `tools/porting/collect_phase2_artifacts.sh`
- `tools/porting/build_anykernel_candidate.sh`
- `tools/porting/write_run_meta.sh`
- `tools/porting/run_postprocess_suite.sh`

Detailed script index:

- `tools/porting/README.md`

## Phase2 artifact guide

After each run, check:

- `artifacts/phase2-report.txt` — single-file summary
- `artifacts/build-exit.txt` — `defconfig_rc` / `build_rc` / `dtbs_rc`
- `artifacts/build-error-summary.txt` — condensed error clues
- `artifacts/anykernel-info.txt` — candidate packaging status
- `artifacts/next-focus.txt` — suggested next optimization direction

Additional diagnostics:

- `artifacts/make-defconfig.log`
- `artifacts/make-build.log`
- `artifacts/make-target-dtbs.log`
- `artifacts/make-dtb-manifest.log`
- `artifacts/dtb-postcheck.txt`
- `artifacts/dtb-miss-analysis.txt`
- `artifacts/phase2-metrics.json`

## Repository layout

- `.github/workflows/` — CI workflows
- `tools/porting/` — migration/analysis tooling
- `porting/` — plans, inventory, reports, changelog

## Documentation

- Porting docs index: `porting/README.md`
- Tooling script index: `tools/porting/README.md`
- Chinese README: `README.zh-CN.md`

## Repository sanity check

Run:

- `python tools/porting/repo_sanity_check.py`

Checks include Python script compilation, workflow script references, and markdown local-link validity.

## Contributing

- Guide: `CONTRIBUTING.md`
- Code owners: `.github/CODEOWNERS`

## License

Licensed under **GNU GPL v2.0**. See `LICENSE`.
