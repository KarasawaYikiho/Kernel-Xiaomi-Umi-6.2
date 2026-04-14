# Tools/Porting

Automation scripts for `Phase2-Port-Umi.yml`.

## Pipeline Order

1. `InstallCiDeps.sh` — Install CI dependencies
2. `PreparePhase2Sources.sh` — Clone source/target
3. `CheckTargetKernelVersion.sh` — Kernel version check
4. `NormalizeBootimgRequiredBytes.sh` — Normalize size input
5. `ApplyPhase2Migration.sh` — Device migration
6. `RunPhase2Build.sh` — Kernel build
7. `CollectPhase2Artifacts.sh` — Collect artifacts
8. `BuildAnykernelCandidate.sh` — Build AnyKernel zip
9. `PrepareReleaseBootimg.sh` — Release boot.img
10. `WriteRunMeta.sh` — Write run metadata
11. `RunPostprocessSuite.sh` — Postprocess chain

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