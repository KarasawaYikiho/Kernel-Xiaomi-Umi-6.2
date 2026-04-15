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

`PrepareReleaseBootimg.sh` resolves stock boot baselines in this order: local/external official ROM package, extracted ROM directory, local non-git `Porting/OfficialRomBaseline/boot.img`, `ROM_BOOTIMG_URL`, then generic `bootimg_prebuilt_url`.

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

- `RepoSanityCheck.py` is the preferred quick gate for script references, markdown links, and required ignore rules.
- `compileall` may refresh local `__pycache__/` entries, which are expected to stay untracked.
- Keep oversized stock `boot.img` files out of git. Pin their size/hash in `Porting/OfficialRomBaseline/Manifest.json` and `BootImageBaseline.env`, then fetch them from ROM inputs or URLs when needed.
