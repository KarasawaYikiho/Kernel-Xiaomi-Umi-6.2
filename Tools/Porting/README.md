# Tools/porting - Script Index

This directory contains the automation chain used by `Phase2-Port-Umi.yml`.

## CI Pipeline Order

1. `Install_Ci_Deps.sh`
   - Installs required CI packages for build/diagnostics and best-effort boot image tooling (`mkbootimg`).
2. `Prepare_Phase2_Sources.sh`
   - Clones source and target trees into `source/` and `target/`.
3. `Check_Target_Kernel_Version.sh`
   - Prints target kernel version tuple from `target/Makefile`.
4. `Apply_Phase2_Migration.sh`
   - Wrapper around `Phase2_Apply.sh` for device-specific migration.
5. `Run_Phase2_Build.sh`
   - Runs defconfig, core build (`Image.gz` + modules), then preferred DTB targets from manifest (fallback to matrix DTB build); writes `artifacts/build-exit.txt` and build logs.
6. `Collect_Phase2_Artifacts.sh`
   - Collects build outputs, resolves primary DTB candidates, packages umi bundle, and writes flash-readiness inputs.
7. `Build_Anykernel_Candidate.sh`
   - Packages AnyKernel3 candidate zip and writes `artifacts/anykernel-info.txt`.
8. `Prepare_Release_Bootimg.sh`
   - Best-effort `boot.img` stage: either builds with `mkbootimg` + ramdisk, or downloads `BOOTIMG_PREBUILT_URL` fallback; both URL inputs support direct files or zip links (best-effort extraction of `ramdisk*.cpio.gz` / `boot.img`). Writes `artifacts/bootimg-build.txt` with explicit blockers if inputs are missing.
   - Detection order summary: system `mkbootimg` -> `$HOME/.local/bin/mkbootimg(.py)` -> source/target embedded script -> `python3 -m mkbootimg` -> best-effort remote `mkbootimg.py` fetch into `artifacts/`.
9. `Validate_Anykernel_Candidate.py`
   - Validates `AnyKernel3-umi-candidate.zip` structure and writes `artifacts/anykernel-validate.txt`.
9. `Build_Phase2_Report.py`  
   - Generates `artifacts/phase2-report.txt`.
10. `Write_Run_Meta.sh`
   - Writes normalized workflow/run/input metadata to `artifacts/run-meta.txt`.
11. Post-processing suite:
   - `Check_Artifact_Completeness.py`
   - `Validate_Anykernel_Candidate.py` (re-run for tolerance when earlier step is skipped/partial)
   - `Validate_Boot_Image.py`
   - `Suggest_Next_Focus.py`
   - `Extract_Build_Errors.py`
   - `Build_Artifact_Index.py`
   - `Summarize_Artifacts_Markdown.py`
   - `Validate_Phase2_Report.py`
   - `Collect_Metrics_Json.py`
   - `Build_Status_Badge_Line.py`
   - `Build_Artifact_Checksums.py`
   - `Build_Action_Validation_Checklist.py`

## Script Categories

- **Source prep orchestration:** `Prepare_Phase2_Sources.sh`, `Check_Target_Kernel_Version.sh`
- **Migration:** `Apply_Phase2_Migration.sh`, `Phase2_Apply.sh` (includes `vendor/qcom` + `vendor/xiaomi` DTS roots and defconfig fallback strategy)
- **DTB matching/diagnostics:** `Build_Dtb_Manifest.py`, `Dtb_Postcheck.py`, `Analyze_Dtb_Miss.py`
- **Readiness/reporting:** `Evaluate_Artifact.py`, `Build_Phase2_Report.py`, `Validate_Phase2_Report.py`, `Validate_Anykernel_Candidate.py`, `Build_Action_Validation_Checklist.py` (includes `runtime_ready` report field)
- **CI artifact UX:** `Build_Artifact_Index.py`, `Summarize_Artifacts_Markdown.py`, `Build_Status_Badge_Line.py`, `Build_Artifact_Checksums.py`
- **Automation metrics:** `Collect_Metrics_Json.py`, `Check_Artifact_Completeness.py`, `Suggest_Next_Focus.py`, `Extract_Build_Errors.py`
- **Build orchestration:** `Run_Phase2_Build.sh` (defconfig/build attempt + exit snapshot)
- **Build artifact orchestration:** `Collect_Phase2_Artifacts.sh` (collect/package primary artifacts after build)
- **AnyKernel packaging orchestration:** `Build_Anykernel_Candidate.sh` (builds candidate AnyKernel zip + diagnostics)
- **Run metadata orchestration:** `Write_Run_Meta.sh` (records run/input metadata)
- **Postprocess orchestration:** `Run_Postprocess_Suite.sh` (runs post-build reporting scripts in CI)
- **Repository sanity checks:** `Repo_Sanity_Check.py` (python compile, workflow script refs, markdown link checks)

## Key Report Signals

- `next_action`: machine-friendly next step (`ready-for-action-test`, `prepare-release-bootimg`, `fix-build-errors`, etc.)
- `runtime_ready`: coarse gate (`yes`/`no`) indicating whether device-side runtime validation should proceed
- `anykernel_validate_status`: structure validation result for `AnyKernel3-umi-candidate.zip`
- `bootimg_status`: release boot image readiness signal (`ok` / `missing` / `size_mismatch`)
- `bootimg_build_status`: boot image build stage result (`ok` / `blocked` / `failed`)
- `bootimg_required_bytes`: final target boot image size (from workflow input, default `268435456`; set `<=0` to disable size check)
- `action-validation-checklist.md`: now includes boot image status/size/required-size snapshot and blocker projection

## Local Dry-Run Notes

Most scripts read from `artifacts/` and write back to `artifacts/`.
`artifacts/` is treated as build output and should stay untracked in git (use CI upload/download for sharing run results).
A typical local validation flow after obtaining logs/artifacts is:

```bash
python3 Tools/Porting/Validate_Anykernel_Candidate.py
python3 Tools/Porting/Build_Phase2_Report.py
python3 Tools/Porting/Check_Artifact_Completeness.py
python3 Tools/Porting/Extract_Build_Errors.py
python3 Tools/Porting/Collect_Metrics_Json.py
python3 Tools/Porting/Build_Action_Validation_Checklist.py
```

> These scripts are intentionally tolerant in CI (`|| true` in workflow), so missing optional files should be reported rather than hard-failing.
