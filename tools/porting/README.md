# tools/porting - Script Index

This directory contains the automation chain used by `phase2-port-umi.yml`.

## Pipeline Order (as used in CI)

1. `install_ci_deps.sh`
   - Installs required CI packages for build and diagnostics.
2. `prepare_phase2_sources.sh`
   - Clones source and target trees into `source/` and `target/`.
3. `check_target_kernel_version.sh`
   - Prints target kernel version tuple from `target/Makefile`.
4. `apply_phase2_migration.sh`
   - Wrapper around `phase2_apply.sh` for device-specific migration.
5. `run_phase2_build.sh`
   - Runs defconfig, core build (`Image.gz` + modules), then preferred DTB targets from manifest (fallback to matrix DTB build); writes `artifacts/build-exit.txt` and build logs.
6. `collect_phase2_artifacts.sh`
   - Collects build outputs, resolves primary DTB candidates, packages umi bundle, and writes flash-readiness inputs.
7. `build_anykernel_candidate.sh`
   - Packages AnyKernel3 candidate zip and writes `artifacts/anykernel-info.txt`.
8. `build_phase2_report.py`  
   - Generates `artifacts/phase2-report.txt`.
9. `write_run_meta.sh`
   - Writes normalized workflow/run/input metadata to `artifacts/run-meta.txt`.
10. Post-processing suite:
   - `check_artifact_completeness.py`
   - `suggest_next_focus.py`
   - `extract_build_errors.py`
   - `build_artifact_index.py`
   - `summarize_artifacts_markdown.py`
   - `validate_phase2_report.py`
   - `collect_metrics_json.py`
   - `build_status_badge_line.py`
   - `build_artifact_checksums.py`

## Script Categories

- **Source prep orchestration:** `prepare_phase2_sources.sh`, `check_target_kernel_version.sh`
- **Migration:** `apply_phase2_migration.sh`, `phase2_apply.sh`
- **DTB matching/diagnostics:** `build_dtb_manifest.py`, `dtb_postcheck.py`, `analyze_dtb_miss.py`
- **Readiness/reporting:** `evaluate_artifact.py`, `build_phase2_report.py`, `validate_phase2_report.py`
- **CI artifact UX:** `build_artifact_index.py`, `summarize_artifacts_markdown.py`, `build_status_badge_line.py`, `build_artifact_checksums.py`
- **Automation metrics:** `collect_metrics_json.py`, `check_artifact_completeness.py`, `suggest_next_focus.py`, `extract_build_errors.py`
- **Build orchestration:** `run_phase2_build.sh` (defconfig/build attempt + exit snapshot)
- **Build artifact orchestration:** `collect_phase2_artifacts.sh` (collect/package primary artifacts after build)
- **AnyKernel packaging orchestration:** `build_anykernel_candidate.sh` (builds candidate AnyKernel zip + diagnostics)
- **Run metadata orchestration:** `write_run_meta.sh` (records run/input metadata)
- **Postprocess orchestration:** `run_postprocess_suite.sh` (runs post-build reporting scripts in CI)
- **Repository sanity checks:** `repo_sanity_check.py` (python compile, workflow script refs, markdown link checks)

## Local Dry-Run Notes

Most scripts read from `artifacts/` and write back to `artifacts/`.
A typical local validation flow after obtaining logs/artifacts is:

```bash
python3 tools/porting/build_phase2_report.py
python3 tools/porting/check_artifact_completeness.py
python3 tools/porting/extract_build_errors.py
python3 tools/porting/collect_metrics_json.py
```

> These scripts are intentionally tolerant in CI (`|| true` in workflow), so missing optional files should be reported rather than hard-failing.
