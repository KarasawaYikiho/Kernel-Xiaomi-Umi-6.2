# Porting Changelog

> Milestone-only changelog for long-term maintainability.

## 2026-03-09
- Added AnyKernel candidate zip packaging in Phase2 workflow (`AnyKernel3-umi-candidate.zip`).
- Strengthened DTS seed filtering and expanded migration statistics (`dts_only_copied`, `dtsi_only_copied`).
- Added broad diagnostic/reporting toolchain (phase2 report, miss analysis, run metadata, completeness checks, error summary, index, markdown summary, validation, metrics, status line, checksums).
- Improved workflow reliability with concurrency control and timeout.
- Removed quality-gate program path to simplify compile flow and reduce maintenance overhead.
- Refined repo documentation and added docs indexes (`porting/README.md`, tooling index updates, quick-start/readability cleanup).

## 2026-03-08
- Initialized 5+ porting orchestrator skeleton.
- Added inventory collection and generated first capability snapshot.
- Started Phase2 with automated defconfig + DTS migration and CI build attempt.
- Added umi-focused artifact packaging and iterative DTB selection/validation improvements.
- Completed Phase0/Phase1 baseline and classification deliverables.
