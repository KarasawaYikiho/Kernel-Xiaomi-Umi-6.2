# Contributing

[中文贡献指南（CONTRIBUTING.zh-CN.md）](./CONTRIBUTING.zh-CN.md)

Thanks for helping improve **Kernel-Xiaomi-Umi**.

## Scope

This repository is a **kernel porting orchestrator** (CI workflows + migration/diagnostic tooling), not a full kernel source tree.

## Before You Start

1. Read `README.md`
2. Read `porting/README.md`
3. Check `PORTING_PLAN.md` and latest `porting/CHANGELOG.md`

## Branching

Follow `porting/BRANCHING.md`:
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
- For diagnostics, add scripts under `tools/porting/` and document them in `tools/porting/README.md`.

## Changelog Policy

- Add concise milestone entries to `porting/CHANGELOG.md`.
- Put verbose historical detail in archive files when needed.

## Security / Safety

- Do not commit secrets/tokens.
- Keep `.gitignore` clean for local noise.
- Treat generated artifacts as disposable unless explicitly tracked.
