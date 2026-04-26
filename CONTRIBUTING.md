# Contributing

Thanks for improving Kernel-Xiaomi-Umi.

## Scope

Kernel source, DTS, defconfig, drivers, GitHub workflows, porting scripts, diagnostics, and documentation.

## Before You Start

1. Read `README.md`
2. Read `PortingPlan.md`
3. Check `Porting/CHANGELOG.md`

## Branch Strategy

- `port/phase*` — Phase work
- `port/hotfix-*` — Urgent fixes

## PR Requirements

- What changed and why
- Validation evidence
- Risk notes for kernel, DTS, defconfig, workflow, and script changes

## Source Rules

Source and reference roles are listed in `README.md` and `Porting/README.md`.

- yefxx is the source baseline
- SO-TS is reference-only for targeted comparisons
- Official ROM artifacts are validation-only, not code donors
- No blind subtree copy
- No proprietary blob import

## Quality

- Update docs when behavior changes
- Require CI evidence
- Keep `CHANGELOG.md` concise
- Follow the repository hygiene rules in `README.md`

## Security

- No secrets in commit
- Keep `.gitignore` clean
