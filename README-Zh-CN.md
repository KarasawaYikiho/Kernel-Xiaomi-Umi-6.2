# Kernel-Xiaomi-Umi

[English](README.md) | 简体中文

Xiaomi 10 (`umi`) 内核迁移编排仓库。CI 驱动从 SO-TS 4.19 迁移到 5+ 基线。

> 本仓库**不是**内核源码树。

## 职责

- GitHub Actions Phase2 迁移自动化
- 结构化诊断与指标
- 可直接刷入的产物交付

## 快速开始

运行 **`ROM-Aligned-Umi-Port.yml`** 工作流后，优先检查下列产物：

| 产物 | 作用 |
|-----|------|
| `artifacts/phase2-report.txt` | 汇总迁移阶段状态与阻塞项 |
| `artifacts/next-focus.txt` | 给出下一步优先处理事项 |
| `artifacts/runtime-validation-summary.md` | 汇总运行验证结果 |
| `artifacts/anykernel-info.txt` | 记录 AnyKernel 打包状态 |

## 输入

| 输入 | 默认值 | 描述 |
|-----|--------|-------------|
| `device` | `umi` | 设备代号 |
| `source_repo` | SO-TS 4.19 仓库 | 源内核 |
| `target_repo` | yefxx 5+ 仓库 | 目标内核 |
| `bootimg_required_bytes` | `134217728` | 目标 boot.img 大小 |
| `bootimg_ramdisk_url` | (可选) | 自定义 ramdisk |
| `bootimg_prebuilt_url` | (可选) | 回退 boot.img URL，优先于提交 stock boot.img 到仓库 |
| `official_rom_zip` | (可选) | 用于对齐基线的官方 ROM zip 路径或 URL |

## 工作流

- **`ROM-Aligned-Umi-Port.yml`** — 主 ROM 对齐迁移流程
- **`Build-Umi-Kernel.yml`** — 参考云端构建

## 仓库清洁约定

- `artifacts/`、`source/`、`target/` 是工作流和本地验证生成的工作目录
- `.ruff_cache/` 与 `__pycache__/` 是本地工具缓存
- 这些路径应保持未跟踪状态，避免污染提交记录
- `Porting/OfficialRomBaseline/` 用于存放可检入的 ROM 基线元数据和小体积校验镜像，供校验流程使用
- 文档阅读顺序见 `Porting/README.md`，本地校验入口见 `Tools/Porting/README.md`

## 参考源

- SO-TS: `android_kernel_xiaomi_sm8250` (4.19)
- 5+ 基线: `yefxx/xiaomi-umi-linux-kernel`
- 驱动参考: `UtsavBalar1231/*`

## 许可证

GPL-2.0-only
