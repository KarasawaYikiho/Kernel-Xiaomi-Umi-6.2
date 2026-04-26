# Branch Policy And Repository Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `main` the non-kernel orchestration branch, make `master` the complete kernel-source branch, persist that policy in repository memory, optimize repository structure, and push both branches.

**Architecture:** `main` keeps project policy, docs, Porting tools, and workflow metadata without imported Linux kernel source. `master` contains the full yefxx-based kernel source plus Porting tooling and is the only branch where kernel build Actions run. Project-owned files use independent-word TitleCase naming where safe; Linux kernel source paths keep upstream lowercase conventions.

**Tech Stack:** Git branches, GitHub Actions, Linux Kbuild, WSL Ubuntu, Python 3, Bash, Markdown repository policy docs.

---

### Task 1: Persist Branch Policy Memory

**Files:**
- Create: `AGENTS.md`
- Modify: `README.md`, `README-Zh-Cn.md`, `Porting/README.md`

- [x] Create `AGENTS.md` documenting branch roles: `main` has no kernel source, `master` has full kernel source, Actions run from `master`, local work may use local kernel source and sync finished work to `master`.
- [x] Add a short branch-policy section to English and Chinese READMEs.
- [x] Link `AGENTS.md` from `Porting/README.md`.

### Task 2: Align GitHub Actions With Master Kernel Branch

**Files:**
- Modify: `.github/workflows/Build-Umi-Kernel.yml`
- Modify: `.github/workflows/ROM-Aligned-Umi-Port.yml`
- Modify: `Porting/Tools/SelftestBuildWorkflow.py`

- [x] Restrict workflow dispatch and push triggers to `master`.
- [x] Keep build commands using checked-out workspace kernel source.
- [x] Keep no external yefxx clone in workflows.
- [x] Update selftest to assert `branches: [master]`, no `kernel` clone, and Kbuild commands exist.

### Task 3: Optimize Project-Owned Naming And References

**Files:**
- Modify project-owned docs and scripts only.
- Do not rename imported Linux kernel source directories/files.

- [x] Keep `Porting/Tools` as project tooling path because root `tools/` belongs to Linux kernel source.
- [x] Rename project-owned docs/plans only when safe and update all references.
- [x] Preserve executable script names consumed by workflows unless all references and tests are updated.
- [x] Run `Porting/Tools/RepoSanityCheck.py` after renames.

### Task 4: Reduce Duplication And Clean Generated Files

**Files:**
- Modify: `README.md`, `README-Zh-Cn.md`, `Porting/README.md`, `Porting/Tools/README.md`, `.gitignore`

- [x] Remove duplicated long explanations; keep branch policy in `AGENTS.md` and reference it.
- [x] Ensure generated `artifacts/`, `out/`, `source/`, `target/`, Python caches, and local ROM inputs stay ignored.
- [x] Remove generated artifact files from the working tree if untracked.

### Task 5: Verify Master Branch Kernel Source State

**Files:**
- Verify only; modify only if checks reveal source-layout problems.

- [x] Run `python Porting/Tools/SelftestBuildWorkflow.py`.
- [x] Run `python Porting/Tools/SelftestDtbManifest.py`.
- [x] Run `python Porting/Tools/SelftestDecisionFlow.py`.
- [x] Run `python Porting/Tools/SelftestPhaseFramework.py`.
- [x] Run `python Porting/Tools/SelftestUmiBuildTargets.py`.
- [x] Run `python Porting/Tools/RepoSanityCheck.py`.
- [x] Run `python -m compileall Porting/Tools`.
- [x] Run WSL Kbuild: `make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 umi_defconfig`.
- [x] Run WSL Kbuild: `make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 qcom/sm8250-xiaomi-umi.dtb`.

### Task 6: Commit And Push Master

**Files:**
- All kernel-source branch changes.

- [x] Create or switch to local `master` without losing current working tree changes.
- [x] Commit full kernel source branch state with a message focused on establishing the yefxx-based kernel-source branch.
- [x] Push `master` to `origin/master`.

### Task 7: Restore Main As Non-Kernel Branch

**Files:**
- Keep: project docs, `.github/`, `Porting/`, `AGENTS.md`, plans/specs if useful.
- Remove from `main`: imported Linux kernel source roots and kernel root files.

- [x] Switch to `main`.
- [x] Remove imported kernel source files/directories from `main` while preserving project-owned docs and tools.
- [x] Keep README branch policy pointing users to `master` for kernel source.
- [x] Run repository sanity checks available on non-kernel `main`.
- [x] Commit and push `main` to `origin/main`.

### Task 8: Final Verification

**Files:**
- Verify branch state and remotes.

- [x] Confirm `origin/master` contains `Makefile`, `arch/`, `drivers/`, `include/`, `kernel/`, `scripts/`, and `tools/`.
- [x] Confirm `origin/main` does not contain imported Linux kernel source roots.
- [x] Confirm workflows are present and target `master`.
- [x] Report pushed commit hashes and any residual risks.
