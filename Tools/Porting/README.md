# Tools/Porting

Automation scripts for `ROM-Aligned-Umi-Port.yml`.

## Pipeline Order

1. `InstallCiDeps.sh` — Install CI dependencies
2. `PreparePhase2Sources.sh` — Clone source/target
3. `AnalyzeOfficialRomPackage.py` — Build ROM baseline evidence
4. `CheckTargetKernelVersion.sh` — Kernel version check
5. `NormalizeBootimgRequiredBytes.sh` — Normalize size input
6. `ApplyPhase2Migration.sh` — Device migration
7. `RunPhase2Build.sh` — Kernel build
8. `CollectPhase2Artifacts.sh` — Collect artifacts
9. `BuildAnykernelCandidate.sh` — Build AnyKernel zip
10. `PrepareReleaseBootimg.sh` — ROM-aware release boot.img
11. `WriteRunMeta.sh` — Write run metadata
12. `RunPostprocessSuite.sh` — Postprocess chain

`PrepareReleaseBootimg.sh` resolves stock boot baselines in this order: `official_rom_zip`, direct `official_bootimg_path`, `official_rom_dir`, local non-git `Porting/OfficialRomBaseline/boot.img`, `ROM_BOOTIMG_PATH`, then generic `bootimg_prebuilt_path`.

## Key Reports

- `next_action` — Next step decision
- `runtime_ready` — Runtime gate
- `driver_integration_pending` — Pending drivers
- `anykernel_validate_status` — AnyKernel validity
- `bootimg_status` — boot.img readiness

## Local Validation

```bash
python Tools/Porting/RepoSanityCheck.py
python Tools/Porting/SelftestDecisionFlow.py
python -m compileall Tools/Porting
```

## Local Official ROM Baseline

```powershell
powershell -ExecutionPolicy Bypass -File "Tools/Porting/RunLocalOfficialRomBaseline.ps1"
```

This is the shortest Windows path for local ROM alignment. It analyzes `OFFICIAL_ROM_DIR`, prepares `artifacts/boot.img`, and validates the result in one command.

Refreshes:

- `Porting/OfficialRomAnalysis.md`
- `artifacts/official-rom-baseline.json`
- `artifacts/boot.img`
- `artifacts/bootimg-info.txt`

- `RepoSanityCheck.py` is the preferred quick gate for script references, markdown links, and required ignore rules.
- `RepoSanityCheck.py` also fails if generated work directories or compiled cache files are tracked in git.
- `compileall` may refresh local `__pycache__/` entries, which are expected to stay untracked.
- Keep oversized stock `boot.img` files out of git. Pin their size/hash in `Porting/OfficialRomBaseline/Manifest.json` and `BootImageBaseline.env`, then point workflows at local ROM inputs or local boot image paths when needed.
- `PrepareReleaseBootimg.sh` now avoids network fallback for boot payloads and resolves `mkbootimg` from the local toolchain or the cloned source/target trees.
- `BuildAnykernelCandidate.sh` now prefers the checked-in `Tools/Porting/AnyKernel3Template/` and no longer needs to clone AnyKernel3 just to produce a candidate zip.
- For local runs, prefer `OFFICIAL_ROM_DIR=D:\GIT\MIUI_UMI` so the extracted ROM directory supplies `boot.img`, `dtbo.img`, and `vbmeta*.img` without committing large binaries.
- `ValidateBootImage.py` now treats official boot reference binding as a hard gate: format, size, header version, and trusted source metadata must all line up before `flash_ready=yes`.
