# Repository Hygiene Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove machine-local paths from tracked content, improve hygiene automation, reduce duplicated path guidance, preserve branch roles, and push both `master` and `main`.

**Architecture:** Project-owned files are optimized while imported kernel source paths stay unchanged. `RepoSanityCheck.py` becomes the durable guard for local path leakage, and docs point users to environment variables instead of machine-specific paths.

**Tech Stack:** Git branches, Python repository sanity tooling, Markdown docs, JSON config, GitHub Actions metadata.

---

### Task 1: Add Local Path Leak Guard

**Files:**
- Modify: `Porting/Tools/RepoSanityCheck.py`

- [x] Run `python Porting/Tools/RepoSanityCheck.py` and confirm it fails before cleanup because tracked files contain local paths.
- [x] Add a tracked-content check that scans `git ls-files` output for Windows drive paths, WSL mount paths, user-home paths, and the local checkout folder name.
- [x] Exclude binary tracked content from text decoding failures by reading with `errors="ignore"`.

### Task 2: Remove Local Paths From Project Content

**Files:**
- Modify: `README.md`
- Modify: `README-Zh-Cn.md`
- Modify: `Porting/Tools/README.md`
- Modify: `Porting/OfficialRomBaseline/README.md`
- Modify: `Porting/OfficialRomAnalysis.md`
- Modify: `Porting/Sm8250PortConfig.json`

- [x] Replace hard-coded local ROM paths with generic environment-variable examples.
- [x] Set local ROM defaults in `Porting/Sm8250PortConfig.json` to empty strings so scripts require explicit local inputs or use tracked baseline artifacts.
- [x] Keep official ROM artifacts validation-only, not source donors.

### Task 3: Verify Master

**Files:**
- Verify only unless checks fail.

- [x] Run `python Porting/Tools/SelftestBuildWorkflow.py`.
- [x] Run `python Porting/Tools/SelftestDtbManifest.py`.
- [x] Run `python Porting/Tools/SelftestDecisionFlow.py`.
- [x] Run `python Porting/Tools/SelftestPhaseFramework.py`.
- [x] Run `python Porting/Tools/SelftestUmiBuildTargets.py`.
- [x] Run `python Porting/Tools/RepoSanityCheck.py`.
- [x] Run `python -m compileall Porting/Tools`.
- [x] Run WSL `make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 umi_defconfig` when available.
- [x] Run WSL `make O=out ARCH=arm64 LLVM=1 LLVM_IAS=1 qcom/sm8250-xiaomi-umi.dtb` when available.

### Task 4: Commit And Push Master

**Files:**
- All modified project-owned files on `master`.

- [x] Remove generated `artifacts/`, `out/`, and Python caches.
- [ ] Commit the optimized master state.
- [ ] Push `origin/master`.

### Task 5: Apply And Push Main

**Files:**
- Same project-owned files that exist on `main`.

- [ ] Switch to `main`.
- [ ] Apply the same project-owned cleanup without adding kernel source.
- [ ] Run non-kernel sanity checks.
- [ ] Confirm `main` lacks imported kernel source roots.
- [ ] Commit and push `origin/main`.

### Task 6: Final Verification

**Files:**
- Verify remote branch state.

- [ ] Confirm `origin/master` contains kernel source roots.
- [ ] Confirm `origin/main` lacks kernel source roots.
- [ ] Confirm no tracked local paths remain on either branch.
- [ ] Report commit hashes and verification evidence.
