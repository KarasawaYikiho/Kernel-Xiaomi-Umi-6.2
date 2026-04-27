# Porting/Tools

Automation scripts for `ROM-Aligned-Umi-Port.yml`.

The workflow auto-fills repository URLs, default branches, toolchain source, local ROM paths, and boot image size baselines in code. Operators should not need to type source/reference repo links, branch baselines, toolchain download links, boot size, or local boot baseline paths into the workflow UI.

## Path Contract

Scripts source `Common.sh` and call `initialize_porting_paths` before touching source or artifact directories.

| Variable | Default | Meaning |
|----------|---------|---------|
| `KERNEL_DIR` | `$PWD` / git root | Checked-out yefxx-based kernel source tree |
| `REFERENCE_DIR` | `$PWD/source` | SO-TS reference checkout |
| `PHASE2_PORT_DIR` | `$PWD/artifacts/phase2` | Migration evidence and phase workspace |
| `OUT_DIR` | `$PWD/out` | Kbuild output directory |
| `ARTIFACTS_DIR` | `$PWD/artifacts` | Workflow artifacts and reports |

`artifacts/` and `out/` are generated ignored directories. `source/` remains a generated reference checkout, not the active kernel source.

## Pipeline Order

1. `InstallCiDeps.sh` — Install CI dependencies
2. `PreparePhase2Sources.sh` — Clone SO-TS reference
3. `AnalyzeOfficialRomPackage.py` — Build ROM baseline evidence
4. `CheckTargetKernelVersion.sh` — Kernel version check
5. `NormalizeBootImgRequiredBytes.sh` — Normalize size input
6. `ApplyPhase2Migration.sh` — Device migration
7. `RunPhase2Build.sh` — Kernel build
8. `CollectPhase2Artifacts.sh` — Collect artifacts
9. `BuildAnyKernelCandidate.sh` — Build AnyKernel zip
10. `PrepareReleaseBootImg.sh` — ROM-aware release boot.img
11. `WriteRunMeta.sh` — Write run metadata
12. `RunPostprocessSuite.sh` — Postprocess chain
13. `ValidatePhase2Report.py` — Final Phase2 gate for CI pass/fail

`PrepareReleaseBootImg.sh` resolves stock boot baselines in this order: `OFFICIAL_ROM_ZIP`, `OFFICIAL_BOOTIMG_PATH`, `OFFICIAL_ROM_DIR`, local non-git `Porting/OfficialRomBaseline/boot.img`, `ROM_BOOTIMG_PATH`, then reconstructed `Porting/OfficialRomBaseline/BootImgParts/` chunks.

## Key Reports

- `plan-progress` — Plan phase/checklist progress derived from `PortingPlan.md` + current artifacts
- `next_action` — Next step decision
- `runtime_ready` — Runtime gate
- `driver_integration_pending` — Pending drivers
- `anykernel_validate_status` — AnyKernel validity
- `bootimg_status` — boot.img readiness
- `phase2_complete` — hard Phase2 completion gate
- `phase2_blockers` — required blockers that prevent runtime/device validation

## Local Validation

```bash
python Porting/Tools/RepoSanityCheck.py
python Porting/Tools/SelftestBuildWorkflow.py
python Porting/Tools/SelftestDtbManifest.py
python Porting/Tools/SelftestDecisionFlow.py
python Porting/Tools/SelftestPhaseFramework.py
python Porting/Tools/SelftestReferenceStrategy.py
python Porting/Tools/SelftestRepoSanityCheck.py
python -m compileall Porting/Tools
```

`RunPostprocessSuite.sh` generates reports even when Phase2 is incomplete. The workflow then runs `ValidatePhase2Report.py` as the final gate so incomplete Phase2 artifacts remain uploaded for debugging while CI still fails when hard gates such as `dtbs_rc=0` are not satisfied.

Real-device runtime validation is not part of Phase2. It remains blocked until Phase2 and Phase3 exit criteria are complete.

## Local Official ROM Baseline

```powershell
powershell -ExecutionPolicy Bypass -File "Porting/Tools/RunLocalOfficialRomBaseline.ps1"
```

This is the local ROM alignment entry point. Set `OFFICIAL_ROM_DIR` or `OFFICIAL_BOOTIMG_PATH` before running it when private stock ROM material is required; otherwise the tracked split baseline remains the portable fallback.

Refreshes:

- `Porting/OfficialRomAnalysis.md`
- `artifacts/official-rom-baseline.json`
- `artifacts/boot.img`
- `artifacts/bootimg-info.txt`

- `RepoSanityCheck.py` is the preferred quick gate for script references, markdown links, and required ignore rules.
- `RepoSanityCheck.py` also fails if generated work directories or compiled cache files are tracked in git.
- `compileall` may refresh local `__pycache__/` entries, which are expected to stay untracked.
- Keep oversized stock `boot.img` files out of git. Pin their size/hash in `Porting/OfficialRomBaseline/Manifest.json` and `BootImageBaseline.env`, then point workflows at local ROM inputs or local boot image paths when needed.
- `PrepareReleaseBootImg.sh` now avoids network fallback for boot payloads and resolves `mkbootimg` from the local toolchain or checked-out source/reference trees.
- `SetupKernelToolchain.sh` resolves the cloud build toolchain from `Porting/Sm8250PortConfig.json`, so workflow YAML no longer carries raw download URLs.
- `MaterializeOfficialBootImg.py` reconstructs the tracked split baseline from `Porting/OfficialRomBaseline/BootImgParts/` when Action cannot access a local ROM directory.
- `BuildAnyKernelCandidate.sh` now prefers the checked-in `Porting/Tools/AnyKernel3Template/` and no longer needs to clone AnyKernel3 just to produce a candidate zip.
- For local runs, prefer `OFFICIAL_ROM_DIR` so the extracted ROM directory supplies `boot.img`, `dtbo.img`, and `vbmeta*.img` without committing large binaries.
- `RefreshOfficialBootImgParts.ps1` regenerates the tracked `BootImgParts/` chunks from a local stock image when maintainers need to update the baseline.
- `ValidateBootImage.py` treats official boot reference binding as a hard gate: format, size, header version, and trusted source metadata must all line up before `flash_ready=yes`.
- Boot artifact readiness is patcher-agnostic: the target is an official-aligned custom boot image that remains compatible with KernelSU, Magisk, or equivalent patchers.
