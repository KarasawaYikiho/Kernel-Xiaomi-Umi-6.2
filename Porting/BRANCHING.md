# Branching Strategy (Porting)

- `main`: integration branch (current default)
- `port/phase0-*`: baseline lock / planning
- `port/phase1-*`: inventory / gap analysis / classification
- `port/phase2-*`: bootable migration (defconfig + dts + build)
- `port/phase3-*`: subsystem feature ports (display/audio/camera/etc.)
- `port/hotfix-*`: urgent CI/packaging fixes

Rule: merge phase branches into `main` only after CI artifact sanity checks.

## Merge Checklist (Recommended)

- [ ] Workflow run completed and artifacts uploaded
- [ ] `phase2-report.txt` is present and readable
- [ ] `build-exit.txt` has expected status for this phase
- [ ] `CHANGELOG.md` updated for meaningful changes
- [ ] README/docs updated if behavior or outputs changed
