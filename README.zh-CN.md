# Kernel-Xiaomi-Umi

Xiaomi 10 (`umi`) 内核迁移编排仓库。CI 驱动从 SO-TS 4.19 迁移到 5+ 基线。

> 本仓库**不是**内核源码树。

## 职责

- GitHub Actions Phase2 迁移自动化
- 结构化诊断与指标
- 可直接刷入的产物交付

## 快速开始

运行 **`Phase2-Port-Umi.yml`** 工作流，然后检查：

1. `artifacts/phase2-report.txt`
2. `artifacts/next-focus.txt`
3. `artifacts/runtime-validation-summary.md`
4. `artifacts/anykernel-info.txt`

## 输入

| 输入 | 默认值 | 描述 |
|-----|--------|-------------|
| `device` | `umi` | 设备代号 |
| `source_repo` | SO-TS 4.19 仓库 | 源内核 |
| `target_repo` | yefxx 5+ 仓库 | 目标内核 |
| `bootimg_required_bytes` | `134217728` | 目标 boot.img 大小 |
| `bootimg_ramdisk_url` | (可选) | 自定义 ramdisk |
| `bootimg_prebuilt_url` | (可选) | 回退 boot.img |

## 工作流

- **`Phase2-Port-Umi.yml`** — 主迁移流程
- **`Build-Umi-Kernel.yml`** — 参考云端构建

## 参考源

- SO-TS: `android_kernel_xiaomi_sm8250` (4.19)
- 5+ 基线: `yefxx/xiaomi-umi-linux-kernel`
- 驱动参考: `UtsavBalar1231/*`

## 许可证

GPL-2.0-only