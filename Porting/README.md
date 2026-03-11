# Porting Docs Index

This directory stores planning, baselines, and progress records for UMI porting.

## Core Files

- `PORTING_PLAN.md` (repo root) — high-level roadmap and phase checklist
- `Baseline-Lock.json` — pinned source/target baseline metadata
- `BRANCHING.md` — branch naming and merge policy
- `Classification-Phase1.md` — Phase 1 classification output
- `Inventory.json` — source/target capability inventory (+ additional reference discovery for UtsavBalar1231/Strawing)
- `Gap-Report.md` — gap analysis summary
- `Reference-Drivers-Analysis.md` — focused driver delta analysis from external reference sources
- `OfficialRom-Umi-Os1.0.5.0-Analysis.md` — official MIUI package metadata/hash/partition-op analysis (non-blob integration)
- `CHANGELOG.md` — concise milestone change history

## Suggested Reading Order

1. `PORTING_PLAN.md`
2. `BRANCHING.md`
3. Latest section in `CHANGELOG.md`
4. `Classification-Phase1.md` and `Gap-Report.md`
5. `Reference-Drivers-Analysis.md`

## Maintenance Notes

- Keep milestone-level updates in `CHANGELOG.md`.
- Avoid duplicating workflow details here; put execution details in `Tools/Porting/README.md`.
