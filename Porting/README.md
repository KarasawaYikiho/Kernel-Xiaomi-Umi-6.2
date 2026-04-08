# Porting Docs Index

This directory stores planning/baseline/analysis records for UMI porting.

## Core Files

- `../PORTING_PLAN.md` — top-level roadmap and phase checklist
- `BaselineLock.json` — pinned source/target metadata
- `BRANCHING.md` — branch naming and merge rules
- `ClassificationPhase1.md` — phase-1 migration classification
- `Inventory.json` — source/target capability inventory
- `GapReport.md` — high-level gap summary
- `ReferenceDriversAnalysis.md` — donor-reference driver analysis
- `OfficialRomAnalysis.md` — official ROM metadata-only analysis
- `CHANGELOG.md` — milestone history

## Suggested Reading Order

1. `../PORTING_PLAN.md`
2. `BRANCHING.md`
3. Latest section in `CHANGELOG.md`
4. `ClassificationPhase1.md`
5. `GapReport.md`
6. `ReferenceDriversAnalysis.md`

## Maintenance Rules

- Keep this folder for planning/analysis docs.
- Put execution/tool details in `../Tools/Porting/README.md`.
- Keep milestone summaries concise; archive verbose logs elsewhere.
