# Branching Strategy (Porting)

- `main`: integration branch (current default)
- `port/phase0-*`: baseline lock / planning
- `port/phase1-*`: inventory / gap analysis / classification
- `port/phase2-*`: bootable migration (defconfig + dts + build)
- `port/phase3-*`: subsystem feature ports (display/audio/camera/etc.)
- `port/hotfix-*`: urgent CI/packaging fixes

Rule: merge phase branches into `main` only after CI artifact sanity checks.
