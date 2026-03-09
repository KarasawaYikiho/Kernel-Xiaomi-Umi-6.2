# tools/porting - Script Index

This directory contains the automation chain used by `phase2-port-umi.yml`.

## Pipeline Order (as used in CI)

1. `phase2_apply.sh`  
   - Migrates `umi_defconfig` and selected DTS/DTSI (include-aware BFS copy).
2. `build_dtb_manifest.py`  
   - Generates `artifacts/target_dtb_manifest.txt` from migrated DTS list.
3. `dtb_postcheck.py`  
   - Computes hit/miss against built DTB/DTBO outputs.
4. `analyze_dtb_miss.py`  
   - Buckets DTB misses for diagnosis.
5. `evaluate_artifact.py`  
   - Emits flash-readiness hints.
6. `build_phase2_report.py`  
   - Generates `artifacts/phase2-report.txt`.
7. `collect_phase2_artifacts.sh`
   - Collects build outputs, resolves primary DTB candidates, packages umi bundle, and writes flash-readiness inputs.
8. Post-processing suite:
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

- **Migration:** `phase2_apply.sh`
- **DTB matching/diagnostics:** `build_dtb_manifest.py`, `dtb_postcheck.py`, `analyze_dtb_miss.py`
- **Readiness/reporting:** `evaluate_artifact.py`, `build_phase2_report.py`, `validate_phase2_report.py`
- **CI artifact UX:** `build_artifact_index.py`, `summarize_artifacts_markdown.py`, `build_status_badge_line.py`, `build_artifact_checksums.py`
- **Automation metrics:** `collect_metrics_json.py`, `check_artifact_completeness.py`, `suggest_next_focus.py`, `extract_build_errors.py`
- **Build artifact orchestration:** `collect_phase2_artifacts.sh` (collect/package primary artifacts after build)
- **Postprocess orchestration:** `run_postprocess_suite.sh` (runs post-build reporting scripts in CI)

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
