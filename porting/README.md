# Porting Docs Index

This directory stores planning, baselines, and progress records for UMI porting.

## Core Files

- `PORTING_PLAN.md` (repo root) — high-level roadmap and phase checklist
- `baseline-lock.json` — pinned source/target baseline metadata
- `BRANCHING.md` — branch naming and merge policy
- `classification-phase1.md` — Phase 1 classification output
- `inventory.json` — source/target capability inventory
- `gap-report.md` — gap analysis summary
- `CHANGELOG.md` — concise milestone change history

## Suggested Reading Order

1. `PORTING_PLAN.md`
2. `BRANCHING.md`
3. Latest section in `CHANGELOG.md`
4. `classification-phase1.md` and `gap-report.md`

## Maintenance Notes

- Keep milestone-level updates in `CHANGELOG.md`.
- Avoid duplicating workflow details here; put execution details in `tools/porting/README.md`.
