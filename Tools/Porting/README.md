# Tools/Porting Script Index

This directory contains the automation chain used by `Phase2-Port-Umi.yml`.

## CI Pipeline Order

1. `Install_Ci_Deps.sh` — install CI dependencies and best-effort bootimg tooling
2. `Prepare_Phase2_Sources.sh` — clone source/target trees into `source/` and `target/`
3. `Check_Target_Kernel_Version.sh` — emit target kernel version tuple
4. `Normalize_Bootimg_Required_Bytes.sh` — normalize `BOOTIMG_REQUIRED_BYTES` input into a safe integer
5. `Apply_Phase2_Migration.sh` — wrapper for device migration
6. `Run_Phase2_Build.sh` — run defconfig/build/DTB attempts and emit `build-exit.txt`
7. `Collect_Phase2_Artifacts.sh` — collect outputs and package umi bundle
8. `Build_Anykernel_Candidate.sh` — build AnyKernel candidate and emit `anykernel-info.txt`
9. `Prepare_Release_Bootimg.sh` — best-effort release `boot.img` path (`ramdisk` build or prebuilt URL fallback)
10. `Fetch_Inventory.py` — collect source/base/reference inventories and author-ID discovery snapshot
11. `Analyze_Reference_Drivers.py` — derive donor-vs-base driver delta focus
12. `Analyze_Official_Rom_Package.py` — generate official ROM baseline evidence report (placeholder when package missing)
13. `Validate_Anykernel_Candidate.py` — structure validation for candidate zip
14. `Init_Driver_Integration_Manifest.py` — initialize a default `driver-integration-manifest.txt` when missing
15. `Sync_Driver_Integration_Manifest.py` — auto-sync manifest backlog with official ROM + reference-driver requirements
16. `Validate_Driver_Integration_Manifest.py` — validate manifest format and emit status/errors
17. `Build_Driver_Integration_Status.py` — build integration gate from reference/ROM baseline + manifest status
18. `Build_Phase2_Report.py` — produce `phase2-report.txt`
19. `Write_Run_Meta.sh` — write normalized run metadata
20. `Run_Postprocess_Suite.sh` — execute report/summary/metrics/consistency/checklist chain

## Script Categories

- Source prep: `Prepare_Phase2_Sources.sh`, `Check_Target_Kernel_Version.sh`
- Input normalization: `Normalize_Bootimg_Required_Bytes.sh`
- Migration: `Apply_Phase2_Migration.sh`, `Phase2_Apply.sh`
- DTB diagnostics: `Build_Dtb_Manifest.py`, `Dtb_Postcheck.py`, `Analyze_Dtb_Miss.py`
- Baseline/reference analysis: `Fetch_Inventory.py`, `Analyze_Reference_Drivers.py`, `Analyze_Official_Rom_Package.py`
- Readiness/reporting: `Phase2_Decision.py`, `Init_Driver_Integration_Manifest.py`, `Sync_Driver_Integration_Manifest.py`, `Validate_Driver_Integration_Manifest.py`, `Build_Driver_Integration_Status.py`, `Build_Phase2_Report.py`, `Validate_Phase2_Report.py`, `Validate_Boot_Image.py`
- Packaging: `Build_Anykernel_Candidate.sh`, `Validate_Anykernel_Candidate.py`, `Prepare_Release_Bootimg.sh`
- Artifact UX: `Build_Artifact_Index.py`, `Summarize_Artifacts_Markdown.py`, `Build_Status_Badge_Line.py`, `Build_Artifact_Checksums.py`
- Metrics/consistency: `Collect_Metrics_Json.py`, `Suggest_Next_Focus.py`, `Verify_Decision_Consistency.py`
- Repo checks: `Repo_Sanity_Check.py`

## Key Report Signals

- `next_action` — machine-friendly next step (`integrate-drivers-phase3`, `ready-for-action-test`, `prepare-release-bootimg`, etc.)
- `runtime_ready` — coarse gate (`yes`/`no`) for device runtime validation
- `anykernel_validate_status` — AnyKernel candidate structure validity
- `bootimg_status` — release boot image readiness (`ok`, `missing`, `size_mismatch`)
- `bootimg_build_status` — boot image stage result (`ok`, `blocked`, `failed`)
- `bootimg_required_bytes` — target size (default `134217728`; `<=0` disables size gate)
- `bootimg_required_bytes_parse` — parse state (`exact`, `default-empty`, `default-invalid`, `unknown`)
- `decision-consistency.txt` — semantic consistency check across report/focus/runtime
- `action-validation-checklist.md` — runtime checklist with blocker snapshot
- `postprocess-status.txt` — per-step postprocess execution status (`ok` / `failed`)
- `driver-integration-manifest.txt` — driver subsystem checklist (`integrated:<item>` / `pending:<item>`)
- `driver-integration-manifest-validate.txt` — manifest format validation result

## Local Dry-Run Notes

Most scripts read/write under `artifacts/`.
Treat `artifacts/` as generated output (not source of truth).

Typical local validation:

```bash
python Tools/Porting/Repo_Sanity_Check.py
python -m compileall Tools/Porting
```
