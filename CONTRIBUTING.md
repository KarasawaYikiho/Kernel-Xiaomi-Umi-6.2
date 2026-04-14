# Contributing

Thanks for improving Kernel-Xiaomi-Umi.

## Scope

Porting orchestrator (workflow + scripts + diagnostics), not kernel source.

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
- Risk notes for workflow/script changes

## Reference Sources

- SO-TS: `android_kernel_xiaomi_sm8250`
- 5+ baseline: `yefxx/xiaomi-umi-linux-kernel`
- Driver refs: `UtsavBalar1231/*`

Rules:
- Author IDs are discovery inputs
- No blind subtree copy
- No proprietary blob import

## Quality

- Update docs when behavior changes
- Require CI evidence
- Keep `CHANGELOG.md` concise

## Security

- No secrets in commit
- Keep `.gitignore` clean