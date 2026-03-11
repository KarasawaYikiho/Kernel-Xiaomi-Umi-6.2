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

> Note: GitHub Actions artifacts are downloaded as `.zip` by design. If you need `boot.img`, download the artifact zip and extract `boot.img` from it.
> Size reminder: zip size is compressed size. Confirm final boot image size using `artifacts/bootimg-info.txt` (`size_bytes`) or by checking extracted `boot.img` file size.

Run **`Phase2-Port-Umi.yml`** with default inputs, then inspect artifacts in this order:

1. `artifacts/phase2-report.txt`
2. `artifacts/build-exit.txt`
3. `artifacts/build-error-summary.txt`
4. `artifacts/anykernel-info.txt`
5. `artifacts/next-focus.txt`

This provides a fast pass/fail + next-action loop.

### `Build-Umi-Kernel.yml`

Reference-style cloud build flow:

1. Install dependencies + setup ccache (including best-effort boot image tooling)
2. Download ZyC Clang 15
3. Clone target kernel repo/branch
4. Run `build.sh` with selected device and optional KernelSU
5. Upload build artifacts

Inputs:

- `kernel_repo`
- `kernel_branch`
- `device` (default: `umi`)
- `ksu` (default: `false`)

### `Phase2-Port-Umi.yml`

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
- `bootimg_required_bytes` (default: `268435456`, i.e. 256MiB; interpreted as final target size, set `<=0` to disable size check)
- `bootimg_ramdisk_url` (optional URL for `ramdisk.cpio.gz`, or a zip that contains a ramdisk payload)
- `bootimg_prebuilt_url` (optional URL for a prebuilt `boot.img`, or a zip that contains `boot.img`)

Quick dispatch guidance:

- Prefer `bootimg_ramdisk_url` when you can provide a trusted `ramdisk.cpio.gz` matching the target device/base.
- Use `bootimg_prebuilt_url` as fallback when ramdisk cannot be provided in CI.
- If both are set, the current pipeline attempts prebuilt fallback first, then mkbootimg path.
- Both URL inputs now support either direct files or zip links (best-effort extraction for `ramdisk*.cpio.gz` / `boot.img`).
- `mkbootimg` is now resolved best-effort (system/user path/embedded script/python module, then remote `mkbootimg.py` fetch).

## Key scripts

Core wrappers / orchestrators:

- `Tools/Porting/Install_Ci_Deps.sh`
- `Tools/Porting/Prepare_Phase2_Sources.sh`
- `Tools/Porting/Check_Target_Kernel_Version.sh`
- `Tools/Porting/Apply_Phase2_Migration.sh`
- `Tools/Porting/Run_Phase2_Build.sh`
- `Tools/Porting/Collect_Phase2_Artifacts.sh`
- `Tools/Porting/Build_Anykernel_Candidate.sh`
- `Tools/Porting/Write_Run_Meta.sh`
- `Tools/Porting/Run_Postprocess_Suite.sh`

Detailed script index:

- `Tools/Porting/README.md`

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
- `Tools/Porting/` — migration/analysis tooling
- `Porting/` — plans, inventory, reports, changelog

## Documentation

- Porting docs index: `Porting/README.md`
- Tooling script index: `Tools/Porting/README.md`
- Chinese README: `README.zh-CN.md`

## Repository sanity check

Run:

- `python Tools/Porting/Repo_Sanity_Check.py`

Checks include Python script compilation, workflow script references, and markdown local-link validity.

## Contributing

- Guide: `CONTRIBUTING.md`
- Code owners: `.github/CODEOWNERS`

## License

Licensed under **GPL-2.0-only** (GNU General Public License v2.0 only). See `LICENSE`.
