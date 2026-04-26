# Kernel Source Repositioning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the repository into a yefxx-based Xiaomi SM8250 kernel source tree that builds from the checked-out workspace and uses SO-TS/official ROM only as references.

**Architecture:** The repository root becomes the Linux kernel source root. Existing `Porting/`, `Porting/Tools/`, and `.github/` assets stay in the tree as migration and validation tooling. CI builds `$GITHUB_WORKSPACE` directly, while SO-TS is fetched only into `REFERENCE_DIR` for evidence and targeted comparisons.

**Tech Stack:** Linux kernel 6.11 source, GitHub Actions, Bash, Python 3, Kbuild, arm64, LLVM/Clang, AnyKernel3 packaging.

---

### Task 1: Import Kernel Source Snapshot

**Files:**
- Preserve: `.github/`, `Porting/`, `Porting/Tools/`, project docs
- Import: `Makefile`, `Kbuild`, `Kconfig`, `arch/`, `drivers/`, `include/`, `kernel/`, `fs/`, `mm/`, `net/`, `scripts/`, `tools/`, and kernel root files from `yefxx/xiaomi-umi-linux-kernel@master`

- [x] Clone `https://github.com/yefxx/xiaomi-umi-linux-kernel.git` branch `master` into a temporary directory outside this repository.
- [x] Copy the kernel snapshot into the repository root without overwriting `.github/`, `Porting/`, `Porting/Tools/`, or project planning docs.
- [x] Merge `.gitignore` and `.gitattributes` manually.
- [x] Verify that `Makefile`, `arch/`, `drivers/`, `include/`, `kernel/`, and `scripts/` exist at the repository root.

### Task 2: Reframe Documentation

**Files:**
- Modify: `README.md`, `README-Zh-Cn.md`, `CONTRIBUTING.md`, `CONTRIBUTING-Zh-Cn.md`, `SECURITY.md`, `PortingPlan.md`, `Porting/README.md`, `Porting/GapReport.md`, `Porting/OfficialRomAlignmentFramework.md`

- [x] Replace orchestrator-only wording with kernel-source wording.
- [x] State that yefxx is the source baseline, SO-TS is reference-only, and official ROM is validation-only.
- [x] Update contribution and security scope to include kernel source, DTS, defconfig, drivers, CI, scripts, and docs.
- [x] Run `python Porting/Tools/RepoSanityCheck.py` and fix documentation-link failures introduced by the rewrite.

### Task 3: Rewire CI To Build Current Workspace

**Files:**
- Modify: `.github/workflows/Build-Umi-Kernel.yml`, `.github/workflows/ROM-Aligned-Umi-Port.yml`, `Porting/Tools/SelftestBuildWorkflow.py`

- [x] Remove external yefxx clone steps from build workflows.
- [x] Build with `make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 umi_defconfig`.
- [x] Build with `make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 -j"$(nproc)" Image.gz modules dtbs`.
- [x] Collect artifacts from `out/`, not `kernel/out/`.
- [x] Update selftest expectations so the workflow fails if it clones `$TARGET_REPO` into `kernel` or `target`.

### Task 4: Introduce In-Repo Path Contract

**Files:**
- Modify: `Porting/Tools/Common.sh`, `Porting/Tools/README.md`

- [x] Add shell helpers for `KERNEL_DIR`, `REFERENCE_DIR`, `PHASE2_PORT_DIR`, `OUT_DIR`, and `ARTIFACTS_DIR`.
- [x] Document that `KERNEL_DIR` defaults to `$PWD` and `REFERENCE_DIR` defaults to `$PWD/source`.
- [x] Keep `artifacts/` and `out/` as generated ignored directories.

### Task 5: Rewire ROM-Aligned Scripts

**Files:**
- Modify: `Porting/Tools/PreparePhase2Sources.sh`, `Porting/Tools/ApplyPhase2Migration.sh`, `Porting/Tools/Phase2Apply.sh`, `Porting/Tools/RunPhase2Build.sh`, `Porting/Tools/CheckTargetKernelVersion.sh`, `Porting/Tools/CollectPhase2Artifacts.sh`, `Porting/Tools/BuildDtbManifest.py`, `Porting/Tools/PrepareReleaseBootimg.sh`, `Porting/Tools/BuildDriverIntegrationEvidence.py`

- [x] Change source preparation so it only fetches the SO-TS reference into `REFERENCE_DIR`.
- [x] Replace hardcoded `target/` with `KERNEL_DIR`.
- [x] Replace hardcoded `source/` with `REFERENCE_DIR`.
- [x] Write migration evidence logs to `PHASE2_PORT_DIR`.
- [x] Preserve artifact file names consumed by existing report scripts.
- [x] Run `python Porting/Tools/SelftestDtbManifest.py`, `python Porting/Tools/SelftestDecisionFlow.py`, and `python -m compileall Porting/Tools`.

### Task 6: Add Initial Umi Build Targets

**Files:**
- Create: `arch/arm64/configs/umi_defconfig`
- Create: `arch/arm64/boot/dts/qcom/sm8250-xiaomi-umi.dts`
- Modify: `arch/arm64/boot/dts/qcom/Makefile`

- [x] Create `umi_defconfig` from yefxx `arch/arm64/configs/defconfig` plus boot-relevant SO-TS intent that is valid in 6.11.
- [x] Add initial Umi DTS following existing `sm8250-xiaomi-*` naming conventions.
- [x] Add `dtb-$(CONFIG_ARCH_QCOM) += sm8250-xiaomi-umi.dtb` to the QCOM DTS Makefile.
- [x] Verify `make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 umi_defconfig`.
- [x] Verify `make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 qcom/sm8250-xiaomi-umi.dtb`.

### Task 7: Verify Phase 2 Readiness

**Files:**
- Modify report scripts only if their assumptions conflict with the new in-repo source layout.

- [x] Run `python Porting/Tools/SelftestBuildWorkflow.py`.
- [x] Run `python Porting/Tools/SelftestDtbManifest.py`.
- [x] Run `python Porting/Tools/SelftestDecisionFlow.py`.
- [x] Run `python Porting/Tools/SelftestPhaseFramework.py`.
- [x] Run `python Porting/Tools/RepoSanityCheck.py`.
- [x] Run `python -m compileall Porting/Tools`.
- [x] Run the local kernel defconfig and DTB build commands if the local toolchain is available.
