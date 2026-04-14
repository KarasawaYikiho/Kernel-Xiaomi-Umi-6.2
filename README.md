# Kernel-Xiaomi-Umi

Kernel porting orchestrator for Xiaomi 10 (`umi`). CI-driven migration from SO-TS 4.19 to 5+ baseline.

> This repo is **not** a kernel source tree.

## Scope

- Phase2 migration automation via GitHub Actions
- Structured diagnostics and metrics
- Flash-ready artifact delivery

## Quick Start

Run **`Phase2-Port-Umi.yml`** workflow, then inspect:

1. `artifacts/phase2-report.txt`
2. `artifacts/next-focus.txt`
3. `artifacts/runtime-validation-summary.md`
4. `artifacts/anykernel-info.txt`

## Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `device` | `umi` | Device codename |
| `source_repo` | SO-TS 4.19 repo | Source kernel |
| `target_repo` | yefxx 5+ repo | Target kernel |
| `bootimg_required_bytes` | `134217728` | Target boot.img size |
| `bootimg_ramdisk_url` | (optional) | Custom ramdisk |
| `bootimg_prebuilt_url` | (optional) | Fallback boot.img |

## Workflows

- **`Phase2-Port-Umi.yml`** — Main migration workflow
- **`Build-Umi-Kernel.yml`** — Reference cloud build

## Reference Sources

- SO-TS: `android_kernel_xiaomi_sm8250` (4.19)
- 5+ baseline: `yefxx/xiaomi-umi-linux-kernel`
- Driver refs: `UtsavBalar1231/*`

## License

GPL-2.0-only