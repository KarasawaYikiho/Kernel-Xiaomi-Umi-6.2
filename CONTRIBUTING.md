# Contributing

[中文贡献指南（CONTRIBUTING.zh-CN.md）](./CONTRIBUTING.zh-CN.md)

Thanks for helping improve **Kernel-Xiaomi-Umi**.

## Scope

This repository is a **kernel porting orchestrator** (CI workflows + migration/diagnostic tooling), not a full kernel source tree.

## Before You Start

1. Read `README.md`
2. Read `Porting/README.md`
3. Check `PORTING_PLAN.md` and latest `Porting/CHANGELOG.md`

## Branching

Follow `Porting/BRANCHING.md`:
- `port/phase*` for phase work
- `port/hotfix-*` for urgent fixes

## Pull Requests

Use the PR template and include:
- clear summary/scope
- validation notes (run/artifacts)
- risk + rollback notes for workflow/script changes

## Change Expectations

- Keep docs updated when outputs/behavior change.
- Prefer reproducible CI outputs over local-only tweaks.
- For diagnostics, add scripts under `Tools/Porting/` and document them in `Tools/Porting/README.md`.

## Changelog Policy

- Add concise milestone entries to `Porting/CHANGELOG.md`.
- Put verbose historical detail in archive files when needed.

## Security / Safety

- Do not commit secrets/tokens.
- Keep `.gitignore` clean for local noise.
- Treat generated artifacts as disposable unless explicitly tracked.
